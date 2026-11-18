"""PPAPI H3 v2 adapter; documentation checked 2026-11-18.

Reference descriptors: role, url; video/audio also duration_seconds, size_bytes.
No inferred idempotency support and no internal submission retries.
"""

import os
import re
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from drama_bot.contracts import (
    GenerationRequest,
    PaidCallsDisabled,
    PollResult,
    Submission,
    UnknownSubmission,
)


class ProviderError(RuntimeError):
    """Permanent provider rejection; messages deliberately exclude response bodies."""


class RetryableProviderError(ProviderError):
    """Safe to retry a read, never an uncertain submission."""


def generation_payload(request: GenerationRequest) -> dict:
    shot = request.shot
    if not 4 <= shot.duration_seconds <= 15:
        raise ValueError("H3 duration must be 4–15 seconds")
    text = shot.prompt
    if shot.dialogue:
        text += "\n人物必须在画面中开口说中文，非旁白。台词：\n" + "\n".join(
            f"{line.speaker_id}：{line.text}" for line in shot.dialogue
        )
    if len(text) > 7000:
        raise ValueError("H3 text exceeds 7000 characters")
    content = [{"type": "text", "text": text}]
    counts = Counter()
    totals = Counter()
    types = {
        "first_frame": "image",
        "last_frame": "image",
        "reference_image": "image",
        "reference_video": "video",
        "reference_audio": "audio",
    }
    limits = {
        "first_frame": 1,
        "last_frame": 1,
        "reference_image": 9,
        "reference_video": 3,
        "reference_audio": 3,
    }
    for ref in request.references:
        role = ref.get("role", "first_frame")
        if role not in types:
            raise ValueError("Unsupported reference role")
        counts[role] += 1
        if counts[role] > limits[role]:
            raise ValueError("Too many references")
        url = ref.get("url", "")
        # Deliberately narrower than vendor: no inline base64 or mm_file inputs.
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            raise ValueError("References require public HTTPS URLs")
        kind = types[role]
        size = ref.get("size_bytes")
        if (
            not isinstance(size, int)
            or not 0 < size <= {"image": 30, "video": 50, "audio": 15}[kind] * 1024**2
        ):
            raise ValueError("Verified reference size required within H3 limit")
        if kind in ("video", "audio"):
            duration = ref.get("duration_seconds")
            if not isinstance(duration, (int, float)) or not 2 <= duration <= 15:
                raise ValueError("Verified reference duration must be 2–15 seconds")
            totals[kind] += duration
            if totals[kind] > 15:
                raise ValueError("Reference duration total exceeds 15 seconds")
        content.append({"type": f"{kind}_url", f"{kind}_url": {"url": url}, "role": role})
    if (counts["first_frame"] or counts["last_frame"]) and any(
        counts[key] for key in ("reference_image", "reference_video", "reference_audio")
    ):
        raise ValueError("Frame and reference modes are mutually exclusive")
    payload = {
        "model": "MiniMax-H3",
        "content": content,
        "duration": shot.duration_seconds,
        "resolution": request.resolution,
    }
    if not (counts["first_frame"] or counts["last_frame"]):
        payload["ratio"] = request.aspect_ratio
    return payload


class H3Provider:
    def __init__(
        self,
        *,
        base_url: str,
        downloader,
        paid_enabled: bool = False,
        authorization_id: str = "",
        reserve_budget: Callable[[str], bool] | None = None,
        client: httpx.Client | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.downloader = downloader
        self.paid_enabled = paid_enabled
        self.authorization_id = authorization_id
        self.reserve_budget = reserve_budget
        self.client = client or httpx.Client(timeout=30, follow_redirects=False, trust_env=False)

    def _headers(self):
        key = os.environ.get("PP_API_KEY", "")
        parts = urlsplit(self.base_url)
        if (
            not key
            or parts.scheme != "https"
            or not parts.hostname
            or parts.username
            or parts.password
        ):
            raise ProviderError("PPAPI HTTPS endpoint and environment credential required")
        return {"Authorization": f"Bearer {key}"}

    def submit(self, request: GenerationRequest) -> Submission:
        if not self.paid_enabled or not self.authorization_id or self.reserve_budget is None:
            raise PaidCallsDisabled("Paid generation disabled")
        payload = generation_payload(request)
        headers = self._headers()
        if not self.reserve_budget(request.job_id):
            raise PaidCallsDisabled("Budget reservation denied")
        try:
            response = self.client.post(
                self.base_url + "/v2/video_generation", headers=headers, json=payload
            )
        except httpx.HTTPError:
            raise UnknownSubmission("Submission transport outcome unknown") from None
        if response.status_code >= 500 or response.status_code in (408, 429):
            raise UnknownSubmission("Submission acceptance unknown")
        if not 200 <= response.status_code < 300:
            raise ProviderError(f"Submission rejected: HTTP {response.status_code}")
        try:
            task_id = response.json()["task_id"]
            if not isinstance(task_id, str) or not task_id.strip():
                raise ValueError()
            return Submission(provider_task_id=task_id)
        except (ValueError, KeyError, TypeError):
            raise UnknownSubmission("Submission response lacks usable task ID") from None

    def poll(self, provider_task_id: str) -> PollResult:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", provider_task_id):
            raise ValueError("Invalid provider task ID")
        try:
            response = self.client.get(
                self.base_url + "/v2/query/video_generation/" + provider_task_id,
                headers=self._headers(),
            )
        except httpx.HTTPError:
            raise RetryableProviderError("Poll transport error") from None
        if response.status_code >= 500 or response.status_code == 429:
            raise RetryableProviderError(f"Poll HTTP {response.status_code}")
        if response.status_code != 200:
            raise ProviderError(f"Poll HTTP {response.status_code}")
        try:
            task = response.json()["task"]
            status = task["status"]
            if status in ("queued", "running"):
                return PollResult(state="pending")
            if status == "failed":
                return PollResult(state="failed", error="provider_generation_failed")
            if status == "succeeded":
                url = task["content"]["url"]
                if not isinstance(url, str) or not url.startswith("https://"):
                    raise ValueError()
                return PollResult(state="succeeded", download_url=url)
        except (ValueError, KeyError, TypeError):
            pass
        raise ProviderError("Malformed or unknown provider task result")

    def download(self, url: str, destination: Path):
        return self.downloader.download(url, destination)
