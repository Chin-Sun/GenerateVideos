import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from drama_bot.app import create_app
from drama_bot.config import Settings
from drama_bot.contracts import QualityEvidence, QualityStatus, ShotSpec


def test_health_is_not_quality_approval():
    response = TestClient(create_app()).get("/healthz")
    assert response.status_code == 200
    assert response.json()["generation_quality"] == "unverified"


def test_safe_defaults():
    settings = Settings(_env_file=None)
    assert settings.paid_calls_enabled is False
    assert settings.max_paid_submissions == 0
    assert settings.allowed_user_ids == ()
    assert settings.allowed_tenant_ids == ()
    assert settings.default_aspect_ratio == "9:16"


def test_quality_never_defaults_to_pass():
    assert not QualityEvidence().approved
    with pytest.raises(ValidationError):
        QualityEvidence(dialogue=QualityStatus.PASSED)
    with pytest.raises(ValidationError):
        QualityEvidence(dialogue=QualityStatus.PASSED, synthetic=True,
                        reviewer="tester", evidence_uri="test://fixture")


def test_shot_contract_duration_and_immutability():
    shot = ShotSpec(shot_id="s1", prompt="角色说中文")
    with pytest.raises(ValidationError):
        shot.prompt = "overwrite"
    with pytest.raises(ValidationError):
        ShotSpec(shot_id="s1", prompt="角色说中文", duration_seconds=60)
