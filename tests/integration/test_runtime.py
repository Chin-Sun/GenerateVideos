from fastapi.testclient import TestClient

from drama_bot.app import create_app
from drama_bot.config import Settings
from drama_bot.demo import run_demo


def test_api_assembly_and_reference_block(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'api.db'}", asset_root=tmp_path / "assets",
                        local_api_token="local-test", local_tenant_id="t", local_user_id="u",
                        local_chat_id="c", allowed_tenant_ids=("t",), allowed_user_ids=("u",))
    with TestClient(create_app(settings)) as client:
        assert client.get("/readyz").json()["database"] == "ok"
        body = {"name": "test", "shots": [{"shot_id": "s1", "prompt": "test",
                "dialogue": [{"speaker_id": "甲", "text": "你好"}]}]}
        assert client.post("/projects", json=body).status_code == 401
        headers = {"Authorization": "Bearer local-test"}
        assert client.post("/projects", json=body, headers=headers).status_code == 201
        body["shots"][0]["reference_asset_ids"] = ["unpublished"]
        response = client.post("/projects", json=body, headers=headers)
        assert response.status_code == 422
        assert "capability_blocked" in response.text


def test_offline_complete_path(tmp_path):
    report = run_demo(tmp_path / "demo")
    assert report["paid_submissions"] == report["network_deliveries"] == 0
    assert len(report["recorded_deliveries"]) == 2
    assert report["unchanged_shots_reused"] == 5
    assert all(59 <= d <= 61 for d in report["render_durations"])
    import json
    import zipfile
    from io import BytesIO

    manifest = json.loads((tmp_path / "demo" / "manifest.json").read_text())
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'demo' / 'drama.db'}",
                        asset_root=tmp_path / "demo" / "assets", local_api_token="test",
                        local_tenant_id="offline-tenant", local_user_id="offline-user",
                        local_chat_id="offline-chat", allowed_tenant_ids=("offline-tenant",),
                        allowed_user_ids=("offline-user",))
    with TestClient(create_app(settings)) as client:
        # Discover project via durable render job rather than trusting report shape.
        from sqlalchemy import select

        from drama_bot.core.models import Job
        with client.app.state.service.sessions() as db:
            project_id = db.scalar(select(Job.project_id))
        response = client.get(f"/projects/{project_id}/export",
                              headers={"Authorization": "Bearer test"})
        assert response.status_code == 200
        with zipfile.ZipFile(BytesIO(response.content)) as archive:
            assert "manifest.json" in archive.namelist()
            assert len(archive.namelist()) == len(manifest["assets"]) + 1
