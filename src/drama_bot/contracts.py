"""Shared immutable transport contracts. Core owns persistence; media owns effects.

Provider output is never evidence of correct Chinese dialogue or lip sync.
Protocols are synchronous: durable scheduling belongs exclusively to core.
"""
from enum import StrEnum
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Identity(FrozenModel):
    tenant_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    chat_id: str = Field(min_length=1)
    message_id: str = Field(min_length=1)


class QualityStatus(StrEnum):
    UNVERIFIED = "unverified"
    PASSED = "passed"
    FAILED = "failed"


class QualityEvidence(FrozenModel):
    dialogue: QualityStatus = QualityStatus.UNVERIFIED
    lip_sync: QualityStatus = QualityStatus.UNVERIFIED
    speaker_identity: QualityStatus = QualityStatus.UNVERIFIED
    reviewer: str | None = None
    evidence_uri: str | None = None
    synthetic: bool = False

    @model_validator(mode="after")
    def require_review(self):
        if (QualityStatus.PASSED in (self.dialogue, self.lip_sync, self.speaker_identity)
                and (self.synthetic or not self.reviewer or not self.evidence_uri)):
            raise ValueError("A pass requires non-synthetic media and explicit review evidence")
        return self

    @property
    def approved(self) -> bool:
        return all(s == QualityStatus.PASSED for s in
                   (self.dialogue, self.lip_sync, self.speaker_identity))


class DialogueLine(FrozenModel):
    speaker_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    language: Literal["zh-CN"] = "zh-CN"


class ShotSpec(FrozenModel):
    shot_id: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    duration_seconds: int = Field(default=10, ge=4, le=15)
    dialogue: tuple[DialogueLine, ...] = ()
    reference_asset_ids: tuple[str, ...] = ()
    selected_asset_id: str | None = None


class GenerationRequest(FrozenModel):
    job_id: str
    version_id: str
    shot: ShotSpec
    aspect_ratio: Literal["9:16", "16:9", "1:1"] = "9:16"
    resolution: Literal["768P", "2K"] = "768P"
    # Internal reference descriptors are not passed directly as PPAPI JSON.
    references: tuple[dict, ...] = ()


class Submission(FrozenModel):
    provider_task_id: str = Field(min_length=1)


class PollResult(FrozenModel):
    state: Literal["pending", "succeeded", "failed"]
    download_url: str | None = None
    error: str | None = None


class AssetResult(FrozenModel):
    path: Path
    sha256: str
    duration_seconds: float = Field(gt=0)
    has_audio: bool
    provenance: Literal["provider", "synthetic", "user"]
    quality: QualityEvidence = Field(default_factory=QualityEvidence)


class RenderRequest(FrozenModel):
    version_id: str
    assets: tuple[AssetResult, ...]
    output_path: Path
    aspect_ratio: Literal["9:16", "16:9", "1:1"] = "9:16"
    target_seconds: float = 60
    tolerance_seconds: float = 5
    preview: bool = False


class PaidCallsDisabled(RuntimeError):
    """No explicit budget/authorization: do not perform a paid request."""


class UnknownSubmission(RuntimeError):
    """A submission may have succeeded. Core must not automatically resubmit."""


class UnsupportedCapability(RuntimeError):
    """An optional real inference capability is not configured."""


class VideoProvider(Protocol):
    def submit(self, request: GenerationRequest) -> Submission: ...
    def poll(self, provider_task_id: str) -> PollResult: ...
    def download(self, url: str, destination: Path) -> AssetResult: ...


class Renderer(Protocol):
    def render(self, request: RenderRequest) -> AssetResult: ...


class DeliveryTransport(Protocol):
    def upload(self, asset: AssetResult) -> str: ...
    def send(self, identity: Identity, file_key: str, delivery_id: str) -> str: ...


class SpeechProvider(Protocol):
    def synthesize(self, line: DialogueLine, destination: Path) -> AssetResult: ...


class LipSyncProvider(Protocol):
    def synchronize(self, video: AssetResult, audio: AssetResult,
                    destination: Path) -> AssetResult: ...
