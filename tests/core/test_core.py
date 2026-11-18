import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from drama_bot.config import Settings
from drama_bot.contracts import (
    AssetResult,
    DialogueLine,
    Identity,
    PollResult,
    QualityEvidence,
    ShotSpec,
    Submission,
)
from drama_bot.core import (
    Conflict,
    CoreService,
    CreationRequest,
    Forbidden,
    LeaseLost,
    PatchRequest,
    Worker,
    build_router,
)
from drama_bot.core.models import Asset, Budget, Delivery, Job


@pytest.fixture
def env(tmp_path):
    now = [1000.0]
    service = CoreService(f"sqlite:///{tmp_path / 'db.sqlite'}", ["u", "other"], ["t"], tmp_path / "assets", clock=lambda: now[0])
    who = Identity(tenant_id="t", user_id="u", chat_id="chat1", message_id="m1")
    return service, who, now


def request(preview=True):
    return CreationRequest(name="对白", preview=preview, target_seconds=20, shots=tuple(
        ShotSpec(shot_id=f"s{i}", prompt="角色面对镜头开口说中文", dialogue=(DialogueLine(speaker_id="甲", text="你好"),))
        for i in range(2)))


def make_asset(service, name="clip", provenance="synthetic"):
    path = service.asset_root / f"{name}.mp4"
    path.write_bytes(b"test-only-not-real-video-" + name.encode())
    return AssetResult(path=path, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), duration_seconds=10,
                       has_audio=True, provenance=provenance)


class FakeProvider:
    def __init__(self, service):
        self.service = service
        self.submits, self.polls, self.downloads = 0, [], 0
        self.fail_submit = False
        self.fail_download = False

    def submit(self, request):
        self.submits += 1
        if self.fail_submit:
            raise TimeoutError("ambiguous")
        return Submission(provider_task_id=f"provider-{request.job_id}")

    def poll(self, task_id):
        self.polls.append(task_id)
        return PollResult(state="succeeded", download_url="https://example.invalid/video")

    def download(self, url, destination):
        self.downloads += 1
        if self.fail_download:
            raise OSError("offline")
        return make_asset(self.service, destination.stem)


class FakeRenderer:
    def __init__(self, service):
        self.service = service
        self.calls = []

    def render(self, request):
        self.calls.append(request)
        return make_asset(self.service, request.output_path.stem)


class FakeTransport:
    def __init__(self):
        self.uploads, self.sent = 0, []
        self.fail_send = False

    def upload(self, asset):
        self.uploads += 1
        return "file-key"

    def send_preview(self, identity, key, delivery_id):
        if self.fail_send:
            raise TimeoutError()
        self.sent.append((identity, delivery_id, "草稿，质量未验证"))
        return "message-id"

    def send(self, *args):
        raise AssertionError("unreviewed final must never send")


def worker(service, enabled=True):
    provider, renderer, transport = FakeProvider(service), FakeRenderer(service), FakeTransport()
    # Explicit synthetic-only test authorization; fake provider cannot access network.
    settings = Settings(paid_calls_enabled=enabled, paid_authorization_id="test-only", max_paid_submissions=20,
                        ppapi_api_key="fake-not-a-secret")
    return Worker(service, provider, renderer, transport, settings)


def drain(w, now, count=12):
    for _ in range(count):
        w.run_once()
        now[0] += 6


def test_event_replay_and_reopen(env):
    s, who, now = env
    one = s.create_project(who, request(), event_id="event1")
    other = CoreService(str(s.engine.url), ["u"], ["t"], s.asset_root, clock=lambda: now[0])
    assert other.create_project(who, request(), event_id="event1") == one
    with s.sessions() as db:
        assert len(list(db.scalars(select(Job)))) == 3


def test_concurrent_event_replay(env):
    s, who, _ = env
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: s.create_project(who, request(), event_id="same"), range(2)))
    assert results[0] == results[1]


def test_lease_recovery_fencing_unknown(env):
    s, who, now = env
    s.create_project(who, request())
    j = s.claim("one", 10)
    s.save_job(j.id, j.lease_token, state="submitting", submission_intent={"test": True})
    now[0] += 11
    s.claim("two", 10)
    assert s.get_job(who, j.id)["state"] == "unknown_submission"
    with pytest.raises(LeaseLost):
        s.save_job(j.id, j.lease_token, state="succeeded")
    with pytest.raises(Conflict):
        s.retry_job(who, j.id)
    s.reconcile_submission(who, j.id, "confirmed-provider-id")
    assert s.get_job(who, j.id)["provider_task_id"] == "confirmed-provider-id"


def test_expired_lease_new_token(env):
    s, who, now = env
    s.create_project(who, request())
    j = s.claim("one", 10)
    now[0] += 11
    newer = s.claim("two", 10)
    assert newer.id == j.id and newer.lease_token != j.lease_token
    with pytest.raises(LeaseLost):
        s.heartbeat(j.id, j.lease_token)


def test_disabled_never_submits(env):
    s, who, now = env
    p = s.create_project(who, request())
    w = worker(s, False)
    drain(w, now, 4)
    assert w.provider.submits == 0
    assert s.get_job(who, p["job_ids"][0])["state"] == "blocked"


def test_ambiguous_submit_never_retried(env):
    s, who, now = env
    p = s.create_project(who, request())
    w = worker(s)
    w.provider.fail_submit = True
    drain(w, now)
    assert w.provider.submits == 2
    assert s.get_job(who, p["job_ids"][0])["state"] == "unknown_submission"
    with s.sessions() as db:
        assert db.get(Budget, "test-only").used == 2


def test_download_retry_preserves_provider_id(env):
    s, who, now = env
    p = s.create_project(who, request())
    w = worker(s)
    w.provider.fail_download = True
    drain(w, now, 4)
    assert w.provider.submits == 2
    for jid in p["job_ids"][:-1]:
        assert s.get_job(who, jid)["state"] == "failed"
        s.retry_job(who, jid)
    w.provider.fail_download = False
    drain(w, now)
    assert w.provider.submits == 2
    assert len(w.provider.polls) == 2
    assert len(w.transport.sent) == 1


def test_restarted_provider_id_polls_without_submit(env):
    s, who, now = env
    s.create_project(who, request())
    j = s.claim("crashed", 10)
    s.save_job(j.id, j.lease_token, state="generating", provider_task_id="saved-id")
    now[0] += 11
    w = worker(s)
    w.run_once()
    assert w.provider.submits == 0
    assert w.provider.polls == ["saved-id"]
    assert s.get_job(who, j.id)["state"] == "succeeded"


def test_patch_immutable_asset_reuse_and_conflict(env):
    s, who, now = env
    p = s.create_project(who, request())
    w = worker(s)
    drain(w, now)
    before = s.get_project(who, p["project_id"])
    patch = PatchRequest(expected_head_version_id=p["version_id"], shot_id="s1", patch={"prompt": "换一个表情"})
    revised = s.patch_version(who, p["project_id"], patch)
    with pytest.raises(Conflict):
        s.patch_version(who, p["project_id"], patch)
    after = s.get_project(who, p["project_id"])
    assert after["versions"][0] == before["versions"][0]
    assert s.get_job(who, revised["job_ids"][0])["result"] == s.get_job(who, p["job_ids"][0])["result"]
    assert s.get_job(who, revised["job_ids"][1])["result"] == {}
    drain(w, now)
    assert w.provider.submits == 3


def test_concurrent_revision_cas(env):
    s, who, _ = env
    p = s.create_project(who, request())
    patch = PatchRequest(expected_head_version_id=p["version_id"], shot_id="s1", patch={"prompt": "新镜头"})
    def change(_):
        try:
            return s.patch_version(who, p["project_id"], patch)
        except Conflict:
            return None
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(change, range(2)))
    assert sum(x is not None for x in results) == 1


def test_project_and_event_authorization(env):
    s, who, _ = env
    p = s.create_project(who, request(), "e")
    attacker = who.model_copy(update={"user_id": "other"})
    for fn, args in [(s.get_project, (p["project_id"],)), (s.get_job, (p["job_ids"][0],)),
                     (s.create_project, (request(), "e"))]:
        with pytest.raises(Forbidden):
            fn(attacker, *args)
    with pytest.raises(Forbidden):
        s.get_project(who.model_copy(update={"tenant_id": "bad"}), p["project_id"])


def test_fixed_recipient_and_draft_label(env):
    s, who, now = env
    s.create_project(who, request())
    s.create_project(who.model_copy(update={"chat_id": "chat2", "message_id": "m2"}), request())
    w = worker(s)
    drain(w, now, 20)
    assert {x[0].chat_id for x in w.transport.sent} == {"chat1", "chat2"}
    assert all("草稿" in x[2] for x in w.transport.sent)


def test_final_quality_gate_and_no_synthetic_review(env):
    s, who, now = env
    s.create_project(who, request(False))
    w = worker(s)
    drain(w, now)
    assert w.transport.uploads == 0
    with s.sessions() as db:
        d = db.scalar(select(Delivery))
        assert d.state == "quality_blocked"
    evidence = QualityEvidence(dialogue="passed", lip_sync="passed", speaker_identity="passed", reviewer="tester", evidence_uri="file:///review")
    with pytest.raises(ValueError):
        s.record_review(d.asset_id, evidence)
    with pytest.raises(Conflict):
        w.release_reviewed_delivery(d.id)


def test_unknown_delivery_does_not_resend(env):
    s, who, now = env
    s.create_project(who, request())
    w = worker(s)
    w.transport.fail_send = True
    drain(w, now)
    with s.sessions() as db:
        d = db.scalar(select(Delivery))
        assert d.state == "unknown_delivery" and d.file_key == "file-key"
    assert w.transport.uploads == 1
    with pytest.raises(Conflict):
        w.retry_delivery(who, d.id)


def test_http_fixed_identity_and_validation(env):
    s, who, _ = env
    app = FastAPI()
    app.include_router(build_router(s, Settings(local_api_token="local-test"), who))
    client = TestClient(app)
    body = request().model_dump(mode="json")
    assert client.post("/projects", json=body).status_code == 401
    headers = {"Authorization": "Bearer local-test"}
    assert client.post("/projects", json={**body, "identity": who.model_dump()}, headers=headers).status_code == 422
    p = client.post("/projects", json=body, headers=headers)
    assert p.status_code == 201
    patch = {"expected_head_version_id": "wrong", "shot_id": "s1", "patch": {"prompt": "新镜头"}}
    assert client.post(f"/projects/{p.json()['project_id']}/versions", json=patch, headers=headers).status_code == 409
    app2 = FastAPI()
    app2.include_router(build_router(s, Settings(local_api_token="local-test")))
    assert TestClient(app2).post("/projects", json=body, headers=headers).status_code == 403


def test_review_promotes_exact_preview_asset(env):
    s, who, now = env
    s.create_project(who, request())
    w = worker(s)
    drain(w, now)
    with s.sessions.begin() as db:
        d = db.scalar(select(Delivery))
        # Simulate a real-provider fixture without making any external calls.
        a = db.get(Asset, d.asset_id)
        a.provenance = "provider"
    evidence = QualityEvidence(dialogue="passed", lip_sync="passed", speaker_identity="passed",
                               reviewer="operator", evidence_uri="file:///review")
    s.record_review(d.asset_id, evidence)
    final_id = w.release_reviewed_delivery(d.id)
    assert w.release_reviewed_delivery(d.id) == final_id
    with s.sessions() as db:
        final = db.get(Delivery, final_id)
        assert final.asset_id == d.asset_id and final.purpose == "final"
        assert final.identity_json == d.identity_json


def test_upload_failure_retries_only_delivery(env):
    s, who, now = env
    s.create_project(who, request())
    w = worker(s)
    upload = w.transport.upload
    w.transport.upload = lambda asset: (_ for _ in ()).throw(OSError())
    drain(w, now)
    with s.sessions() as db:
        d = db.scalar(select(Delivery))
        assert d.state == "failed"
    w.transport.upload = upload
    w.retry_delivery(who, d.id)
    drain(w, now)
    assert w.provider.submits == 2
    assert len(w.renderer.calls) == 1 and len(w.transport.sent) == 1


def test_export_hashes_and_missing_asset(env):
    s, who, now = env
    p = s.create_project(who, request())
    w = worker(s)
    drain(w, now)
    manifest = s.export_project(who, p["project_id"])
    assert len(manifest["assets"]) == 3
    Path(manifest["assets"][0]["path"]).write_bytes(b"corrupted")
    with pytest.raises(Conflict):
        s.export_project(who, p["project_id"])


@pytest.mark.parametrize("stage", ["download", "render"])
@pytest.mark.parametrize("hard_crash", [True, False])
def test_published_output_retry_uses_new_attempt(env, stage, hard_crash):
    """Publish then die before registration; immutable orphan must not block recovery."""
    s, who, now = env
    created = s.create_project(who, request())
    w = worker(s)
    if stage == "render":
        w.run_once()
        w.run_once()
    original = w.provider.download if stage == "download" else w.renderer.render
    published = []

    def publish_then_crash(*args):
        path = args[1] if stage == "download" else args[0].output_path
        assert not path.exists(), "adapter must never overwrite an existing output"
        original(*args)
        published.append((path, path.read_bytes()))
        if hard_crash:
            raise SystemExit("simulated process death after atomic file publication")
        raise OSError("simulated failure after atomic file publication")

    if stage == "download":
        w.provider.download = publish_then_crash
    else:
        w.renderer.render = publish_then_crash
    if hard_crash:
        with pytest.raises(SystemExit):
            w.run_once()
    else:
        w.run_once()
    with s.sessions() as db:
        failed = db.scalar(select(Job).where(Job.state == ("downloading" if stage == "download" else "rendering"))) if hard_crash else db.scalar(select(Job).where(Job.state == "failed"))
        jid, token = failed.id, failed.lease_token
        assert not list(db.scalars(select(Asset).where(Asset.path == str(published[0][0]))))
    if not hard_crash:
        s.retry_job(who, jid)
    now[0] += 121
    def immutable_retry(*args):
        path = args[1] if stage == "download" else args[0].output_path
        assert not path.exists(), "retry must use a new immutable output path"
        return original(*args)

    if stage == "download":
        w.provider.download = immutable_retry
    else:
        w.renderer.render = immutable_retry
    drain(w, now)
    recovered = s.get_job(who, jid)
    assert recovered["state"] == "succeeded"
    with pytest.raises(LeaseLost):
        s.save_job(jid, token, state="failed")
    with s.sessions() as db:
        asset = db.get(Asset, recovered["result"]["asset_id"])
        assert asset.path != str(published[0][0])
        assert jid in asset.path
        assert len(list(db.scalars(select(Delivery)))) == 1
    assert published[0][0].read_bytes() == published[0][1]
    assert w.provider.submits == 2  # no paid resubmission for the crashed shot
    # A restart AFTER the successful registration must reuse assets and never redo work.
    calls = (w.provider.downloads, len(w.renderer.calls))
    drain(w, now)
    assert calls == (w.provider.downloads, len(w.renderer.calls))
    manifest = s.export_project(who, created["project_id"])
    assert len(manifest["assets"]) == 3


def test_render_lease_takeover_rolls_back_stale_asset_registration(env):
    s, who, now = env
    s.create_project(who, request())
    w = worker(s)
    w.run_once()
    w.run_once()
    original = w.renderer.render
    orphan = []
    successor = []

    def publish_and_takeover(req):
        result = original(req)
        orphan.append(result.path)
        now[0] += 121
        successor.append(s.claim("successor", 120))
        return result  # stale worker now tries register_asset + fenced success

    w.renderer.render = publish_and_takeover
    w.run_once()
    with s.sessions() as db:
        assert not list(db.scalars(select(Asset).where(Asset.path == str(orphan[0]))))
        assert not list(db.scalars(select(Delivery)))
    w.renderer.render = original
    w._render(successor[0])
    assert s.get_job(who, successor[0].id)["state"] == "succeeded"
    assert orphan[0].exists()
    assert w.renderer.calls[-1].output_path != orphan[0]
    assert w.provider.submits == 2
