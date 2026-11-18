"""FFmpeg timeline composition. No voice replacement, speed changes or silent fallback."""

import hashlib
import json
import math
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from drama_bot.contracts import AssetResult, QualityEvidence, RenderRequest


class MediaValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ProbeInfo:
    duration_seconds: float
    has_audio: bool
    width: int
    height: int


def file_hash(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def probe(path: Path, *, timeout: float = 30) -> ProbeInfo:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-protocol_whitelist",
                "file,pipe",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(path.resolve()),
            ],
            capture_output=True,
            check=True,
            timeout=timeout,
        )
        data = json.loads(result.stdout)
        video = next(s for s in data["streams"] if s["codec_type"] == "video")
        duration = float(data["format"]["duration"])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError()
        audio = [s for s in data["streams"] if s["codec_type"] == "audio"]
        # Refuse significantly truncated audio instead of silently padding dialogue.
        if audio and "duration" in audio[0] and float(audio[0]["duration"]) < duration - 0.25:
            raise MediaValidationError("Audio shorter than video timeline")
        return ProbeInfo(duration, bool(audio), int(video["width"]), int(video["height"]))
    except (subprocess.SubprocessError, OSError, ValueError, KeyError, StopIteration):
        raise MediaValidationError("Unreadable video or invalid audio timeline") from None


class FFmpegRenderer:
    def __init__(self, *, subtitle_srt: Path | None = None, timeout: float = 600):
        self.subtitle_srt = subtitle_srt
        self.timeout = timeout

    def render(self, request: RenderRequest) -> AssetResult:
        if not request.assets:
            raise MediaValidationError("No input shots")
        synthetic = any(a.provenance == "synthetic" or a.quality.synthetic for a in request.assets)
        if synthetic and not request.preview:
            raise MediaValidationError("Synthetic fixtures require explicit preview")
        output = request.output_path.resolve()
        if output.exists() or any(output == a.path.resolve() for a in request.assets):
            raise MediaValidationError("Immutable render output already exists")
        infos = []
        for asset in request.assets:
            if file_hash(asset.path) != asset.sha256:
                raise MediaValidationError("Input asset hash mismatch")
            info = probe(asset.path)
            if not info.has_audio or not asset.has_audio:
                raise MediaValidationError("Dialogue audio track required")
            infos.append(info)
        duration = sum(info.duration_seconds for info in infos)
        if abs(duration - request.target_seconds) > request.tolerance_seconds:
            raise MediaValidationError("Actual timeline outside requested duration tolerance")
        output.parent.mkdir(parents=True, exist_ok=True)
        width, height = {"9:16": (432, 768), "16:9": (768, 432), "1:1": (768, 768)}[
            request.aspect_ratio
        ]
        with tempfile.TemporaryDirectory(dir=output.parent) as directory:
            temp = Path(directory) / "render.mp4"
            cmd = ["ffmpeg", "-nostdin", "-v", "error"]
            for asset in request.assets:
                cmd += ["-protocol_whitelist", "file,pipe", "-i", str(asset.path.resolve())]
            if self.subtitle_srt is not None:
                cmd += ["-protocol_whitelist", "file,pipe", "-i", str(self.subtitle_srt.resolve())]
            filters = []
            labels = []
            for i in range(len(infos)):
                filters += [
                    (
                        f"[{i}:v:0]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,"
                        f"setpts=PTS-STARTPTS[v{i}]"
                    ),
                    (
                        f"[{i}:a:0]aresample=48000,aformat=channel_layouts=stereo,"
                        f"asetpts=PTS-STARTPTS[a{i}]"
                    ),
                ]
                labels.append(f"[v{i}][a{i}]")
            filters.append("".join(labels) + f"concat=n={len(infos)}:v=1:a=1[v][a]")
            cmd += [
                "-filter_complex",
                ";".join(filters),
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
            ]
            if self.subtitle_srt is not None:
                cmd += [
                    "-map",
                    f"{len(infos)}:s:0",
                    "-c:s",
                    "mov_text",
                    "-metadata:s:s:0",
                    "language=zho",
                    "-metadata",
                    "subtitle=embedded_srt",
                ]
            else:
                cmd += ["-metadata", "subtitle=none"]
            if synthetic:
                cmd += ["-metadata", "comment=SYNTHETIC TEST FIXTURE - NOT GENERATED DRAMA"]
            cmd += ["-movflags", "+faststart", str(temp)]
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=self.timeout)
            except (OSError, subprocess.SubprocessError):
                raise MediaValidationError("FFmpeg composition failed") from None
            actual = probe(temp)
            if not actual.has_audio or abs(actual.duration_seconds - duration) > 0.3:
                raise MediaValidationError("Rendered timeline/audio validation failed")
            digest = file_hash(temp)
            os.link(temp, output)
        # Re-render is new evidence, never inherit an approval from source clips.
        return AssetResult(
            path=output,
            sha256=digest,
            duration_seconds=actual.duration_seconds,
            has_audio=True,
            provenance="synthetic" if synthetic else "provider",
            quality=QualityEvidence(synthetic=synthetic),
        )
