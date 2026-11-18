"""All generated media here are SYNTHETIC TEST FIXTURES, not model/dialogue evidence."""

import shutil
import subprocess

import pytest

from drama_bot.contracts import AssetResult, QualityEvidence, RenderRequest
from drama_bot.media.video import FFmpegRenderer, MediaValidationError, file_hash, probe

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="FFmpeg required")


def fixture_asset(path, *, audio=True):
    command = [
        "ffmpeg",
        "-nostdin",
        "-v",
        "error",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=160x90:r=24:d=10",
    ]
    if audio:
        command += ["-f", "lavfi", "-i", "sine=frequency=440:duration=10"]
    command += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
    if audio:
        command += ["-c:a", "aac"]
    command += ["-metadata", "comment=SYNTHETIC TEST FIXTURE", str(path)]
    subprocess.run(command, check=True, capture_output=True, timeout=30)
    info = probe(path)
    return AssetResult(
        path=path,
        sha256=file_hash(path),
        duration_seconds=info.duration_seconds,
        has_audio=info.has_audio,
        provenance="synthetic",
        quality=QualityEvidence(synthetic=True),
    )


def test_real_ffmpeg_sixty_seconds_and_subtitle_rerender(tmp_path):
    original = fixture_asset(tmp_path / "synthetic.mp4")
    req = RenderRequest(
        version_id="v1", assets=(original,) * 6, output_path=tmp_path / "v1.mp4", preview=True
    )
    result = FFmpegRenderer().render(req)
    assert result.has_audio and abs(result.duration_seconds - 60) < 0.3
    assert result.provenance == "synthetic" and not result.quality.approved
    assert file_hash(original.path) == original.sha256
    srt = tmp_path / "subtitles.srt"
    srt.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\n合成测试素材，不代表真实人物开口\n", encoding="utf-8"
    )
    result2 = FFmpegRenderer(subtitle_srt=srt).render(
        req.model_copy(update={"version_id": "v2", "output_path": tmp_path / "v2.mp4"})
    )
    assert result2.sha256 != result.sha256
    assert result.path.exists() and original.path.exists()
    with pytest.raises(MediaValidationError, match="Synthetic"):
        FFmpegRenderer().render(req.model_copy(update={"preview": False}))
    with pytest.raises(MediaValidationError, match="tolerance"):
        FFmpegRenderer().render(
            req.model_copy(update={"assets": (original,), "output_path": tmp_path / "short.mp4"})
        )


@pytest.mark.parametrize("preview", [True, False])
def test_provider_metadata_both_render_modes_mocked(tmp_path, monkeypatch, preview):
    # Pure unit contract test: mocked bytes/probe, NEVER real provider footage or delivery.
    from drama_bot.media import video

    source = tmp_path / "mock-provider.bin"
    source.write_bytes(b"MOCK ONLY")
    asset = AssetResult(
        path=source,
        sha256=file_hash(source),
        duration_seconds=10,
        has_audio=True,
        provenance="provider",
    )
    monkeypatch.setattr(video, "probe", lambda _: video.ProbeInfo(10, True, 160, 90))

    def fake_run(command, **kwargs):
        from pathlib import Path

        Path(command[-1]).write_bytes(b"MOCK RENDER ONLY - NEVER DELIVER")

    monkeypatch.setattr(video.subprocess, "run", fake_run)
    result = FFmpegRenderer().render(
        RenderRequest(
            version_id="mock",
            assets=(asset,),
            output_path=tmp_path / "mock-output.bin",
            target_seconds=10,
            preview=preview,
        )
    )
    assert result.has_audio and not result.quality.approved


def test_missing_audio_is_rejected(tmp_path):
    original = fixture_asset(tmp_path / "silent.mp4", audio=False)
    req = RenderRequest(
        version_id="v", assets=(original,) * 6, output_path=tmp_path / "out.mp4", preview=True
    )
    with pytest.raises(MediaValidationError, match="audio"):
        FFmpegRenderer().render(req)
