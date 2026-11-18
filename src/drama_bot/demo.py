"""Offline fixtures only: real FFmpeg, durable core, fake provider and fake delivery."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

from sqlalchemy import select

from drama_bot.config import Settings
from drama_bot.contracts import AssetResult, DialogueLine, Identity, QualityEvidence, ShotSpec
from drama_bot.core.models import Delivery, Job
from drama_bot.core.service import CreationRequest, PatchRequest
from drama_bot.core.worker import Worker
from drama_bot.media.video import FFmpegRenderer, file_hash, probe
from drama_bot.runtime import service_for


class FixtureProvider:
    def __init__(self, fixture):
        self.fixture = fixture

    def submit(self, request):
        raise AssertionError("offline demo must never submit, even to a fake paid endpoint")

    def poll(self, task_id):
        from drama_bot.contracts import PollResult
        return PollResult(state="succeeded", download_url="fixture://local")

    def download(self, url, destination):
        shutil.copyfile(self.fixture, destination)
        return AssetResult(path=destination, sha256=file_hash(destination), duration_seconds=10,
                           has_audio=True, provenance="synthetic",
                           quality=QualityEvidence(synthetic=True))


class RecordingTransport:
    def __init__(self):
        self.sent = []

    def upload(self, asset):
        assert asset.provenance == "synthetic"
        return "offline-fixture-" + asset.sha256

    def send_preview(self, identity, file_key, delivery_id):
        self.sent.append({"identity": identity.model_dump(), "delivery_id": delivery_id,
                          "label": "SYNTHETIC OFFLINE TEST; NOT CHINESE DRAMA"})
        return "offline-message-" + delivery_id


def run_demo(root: Path):
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    fixture = root / "fixture.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc2=size=144x256:rate=24", "-f", "lavfi", "-i",
                    "sine=frequency=440:sample_rate=48000", "-t", "10", "-c:v", "libx264",
                    "-preset", "ultrafast", "-c:a", "aac", str(fixture)], check=True)
    settings = Settings(database_url=f"sqlite:///{root / 'drama.db'}", asset_root=root / "assets",
                        allowed_user_ids=("offline-user",), allowed_tenant_ids=("offline-tenant",))
    service = service_for(settings)
    identity = Identity(tenant_id="offline-tenant", user_id="offline-user",
                        chat_id="offline-chat", message_id="offline-event")
    shots = tuple(ShotSpec(shot_id=f"s{i}", prompt="离线测试图，不是剧情视频",
                          dialogue=(DialogueLine(speaker_id="甲", text="测试文本，不是真实语音。"),))
                  for i in range(6))
    created = service.create_project(identity, CreationRequest(name="OFFLINE SYNTHETIC", shots=shots),
                                     event_id="offline-event")
    duplicate = service.create_project(identity, CreationRequest(name="duplicate", shots=shots),
                                       event_id="offline-event")
    assert created["project_id"] == duplicate["project_id"]
    transport = RecordingTransport()

    def finish(version_id):
        # Simulate recovery of already-known fixture task IDs. No budget bypass or live submit.
        with service.sessions.begin() as db:
            for job in db.scalars(select(Job).where(Job.version_id == version_id,
                                                    Job.kind == "generate", Job.state == "queued")):
                job.provider_task_id, job.state = "fixture-" + job.id, "generating"
        for _ in range(30):
            # Reconstruct worker each iteration: the DB, not object lifetime, holds progress.
            worker = Worker(service, FixtureProvider(fixture), FFmpegRenderer(), transport, settings)
            worker.run_once()
            with service.sessions() as db:
                delivery = db.scalar(select(Delivery).where(Delivery.version_id == version_id))
                if delivery and delivery.state == "succeeded":
                    return
                failures = list(db.scalars(select(Job).where(Job.version_id == version_id,
                                                              Job.state.in_(["failed", "blocked"]))))
                assert not failures, [j.error_json for j in failures]
        raise AssertionError("demo did not complete")

    finish(created["version_id"])
    revised = service.patch_version(identity, created["project_id"], PatchRequest(
        expected_head_version_id=created["version_id"], shot_id="s2",
        patch={"dialogue": [{"speaker_id": "甲", "text": "修改文本，仍不是真实语音。"}]}))
    finish(revised["version_id"])
    with service.sessions() as db:
        def results(vid):
            return {j.shot_id: j.result_json for j in db.scalars(select(Job).where(Job.version_id == vid))}
        before, after = results(created["version_id"]), results(revised["version_id"])
        assert all(before[s]["asset_id"] == after[s]["asset_id"] for s in before if s not in (None, "s2"))
        assert before["s2"]["asset_id"] != after["s2"]["asset_id"]
    manifest = service.export_project(identity, created["project_id"], revised["version_id"])
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    renders = list((root / "assets").glob("*.mp4"))
    durations = [probe(p).duration_seconds for p in renders]
    report = {"synthetic": True, "quality": "unverified", "paid_submissions": 0,
              "network_deliveries": 0, "recorded_deliveries": transport.sent,
              "versions": [created["version_id"], revised["version_id"]],
              "render_durations": [d for d in durations if d > 50],
              "unchanged_shots_reused": 5}
    assert len(report["render_durations"]) == 2
    (root / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    service.engine.dispose()
    return report


def main():
    parser = argparse.ArgumentParser(description="No network; output folder must not exist")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
