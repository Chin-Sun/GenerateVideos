import httpx
import pytest

from drama_bot.contracts import GenerationRequest, PaidCallsDisabled, ShotSpec, UnknownSubmission
from drama_bot.media.provider import H3Provider, ProviderError, generation_payload


def request(**kwargs):
    return GenerationRequest(
        job_id="job1",
        version_id="v1",
        shot=ShotSpec(shot_id="s1", prompt="人物面对面说中文"),
        **kwargs,
    )


def provider(handler, monkeypatch, **kwargs):
    monkeypatch.setenv("PP_API_KEY", "test-secret-not-real")
    return H3Provider(
        base_url="https://mock.example",
        downloader=None,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        **kwargs,
    )


def test_disabled_and_denied_never_request(monkeypatch):
    calls = []

    def handler(req):
        calls.append(req)
        return httpx.Response(200, json={"task_id": "x"})

    for kwargs in (
        {},
        {"paid_enabled": True, "authorization_id": "test", "reserve_budget": lambda _: False},
    ):
        with pytest.raises(PaidCallsDisabled):
            provider(handler, monkeypatch, **kwargs).submit(request())
    assert not calls


def test_submit_and_poll_exact_contract(monkeypatch):
    calls, budget = [], []

    def handler(req):
        calls.append(req)
        if req.method == "POST":
            assert budget == ["job1"]
            assert req.url.path == "/v2/video_generation"
            assert req.headers["Authorization"] == "Bearer test-secret-not-real"
            return httpx.Response(200, json={"task_id": "id-1"})
        assert req.url.path == "/v2/query/video_generation/id-1"
        return httpx.Response(
            200,
            json={"task": {"status": "succeeded", "content": {"url": "https://cdn.example/a.mp4"}}},
        )

    p = provider(
        handler,
        monkeypatch,
        paid_enabled=True,
        authorization_id="mock-only",
        reserve_budget=lambda job: budget.append(job) is None,
    )
    assert p.submit(request()).provider_task_id == "id-1"
    assert p.poll("id-1").state == "succeeded"
    assert len(calls) == 2


@pytest.mark.parametrize(
    "status,expected", [("queued", "pending"), ("running", "pending"), ("failed", "failed")]
)
def test_poll_states(monkeypatch, status, expected):
    p = provider(lambda _: httpx.Response(200, json={"task": {"status": status}}), monkeypatch)
    assert p.poll("x").state == expected


@pytest.mark.parametrize(
    "response", [httpx.Response(200, json={}), httpx.Response(502), httpx.Response(429)]
)
def test_ambiguous_submission_not_retried(monkeypatch, response):
    calls = []
    p = provider(
        lambda req: calls.append(req) or response,
        monkeypatch,
        paid_enabled=True,
        authorization_id="mock",
        reserve_budget=lambda _: True,
    )
    with pytest.raises(UnknownSubmission):
        p.submit(request())
    assert len(calls) == 1


def test_transport_ambiguity(monkeypatch):
    def handler(req):
        raise httpx.ReadTimeout("SECRET", request=req)

    p = provider(
        handler,
        monkeypatch,
        paid_enabled=True,
        authorization_id="mock",
        reserve_budget=lambda _: True,
    )
    with pytest.raises(UnknownSubmission, match="unknown") as exc:
        p.submit(request())
    assert "SECRET" not in str(exc.value)


def test_references_and_limits():
    frame = {"role": "first_frame", "url": "https://cdn.example/a.jpg", "size_bytes": 100}
    audio = {
        "role": "reference_audio",
        "url": "https://cdn.example/a.mp3",
        "size_bytes": 100,
        "duration_seconds": 8,
    }
    assert "ratio" not in generation_payload(request(references=(frame,)))
    with pytest.raises(ValueError, match="mutually exclusive"):
        generation_payload(request(references=(frame, audio)))
    with pytest.raises(ValueError, match="total"):
        generation_payload(request(references=(audio, audio)))
    with pytest.raises(ValueError, match="Too many"):
        generation_payload(request(references=(frame, frame)))
    for duration in (4, 15):
        assert (
            generation_payload(
                request().model_copy(
                    update={"shot": ShotSpec(shot_id="s", prompt="x", duration_seconds=duration)}
                )
            )["duration"]
            == duration
        )
    with pytest.raises(ValueError):
        ShotSpec(shot_id="s", prompt="x", duration_seconds=16)


def test_bad_state_and_task_path(monkeypatch):
    p = provider(lambda _: httpx.Response(200, json={"task": {"status": "alien"}}), monkeypatch)
    with pytest.raises(ProviderError):
        p.poll("x")
    with pytest.raises(ValueError):
        p.poll("../secret")
