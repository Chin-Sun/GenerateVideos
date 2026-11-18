"""Loopback-only development API; fixed identity injected by trusted assembly."""
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import Response
from pydantic import ValidationError

from drama_bot.contracts import Identity

from .service import Conflict, CreationRequest, Forbidden, PatchRequest


def build_router(service, settings, local_identity: Identity | None = None):
    router = APIRouter()

    def identity(authorization: str | None = Header(default=None)):
        token = settings.local_api_token
        if not token or not authorization or not secrets.compare_digest(authorization, "Bearer " + token.get_secret_value()):
            raise HTTPException(401, "需要本地 Bearer token")
        if local_identity is None:
            raise HTTPException(403, "未配置固定本地身份；不能信任请求体身份")
        try:
            service.authorize(local_identity)
        except Forbidden as exc:
            raise HTTPException(403, str(exc)) from None
        return local_identity

    def call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Forbidden as exc:
            raise HTTPException(403, str(exc)) from None
        except Conflict as exc:
            raise HTTPException(409, str(exc)) from None
        except (ValueError, ValidationError) as exc:
            raise HTTPException(422, str(exc)) from None

    @router.post("/projects", status_code=201)
    def create(request: CreationRequest, who=Depends(identity)):
        return call(service.create_project, who, request)

    @router.get("/projects/{project_id}")
    def project(project_id: str, who=Depends(identity)):
        return call(service.get_project, who, project_id)

    @router.post("/projects/{project_id}/versions", status_code=201)
    def patch(project_id: str, request: PatchRequest, who=Depends(identity)):
        return call(service.patch_version, who, project_id, request)

    @router.get("/jobs/{job_id}")
    def job(job_id: str, who=Depends(identity)):
        return call(service.get_job, who, job_id)

    @router.post("/jobs/{job_id}/retry")
    def retry(job_id: str, who=Depends(identity)):
        call(service.retry_job, who, job_id)
        return {"state": "queued"}

    @router.get("/projects/{project_id}/export")
    def export(project_id: str, version_id: str | None = None, who=Depends(identity)):
        import io
        import json
        import zipfile
        from pathlib import Path
        manifest = call(service.export_project, who, project_id, version_id)
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for asset in manifest["assets"]:
                path = Path(asset["path"])
                relative = f"assets/{asset['id']}.mp4"
                archive.write(path, relative)
                asset["path"] = relative
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        return Response(output.getvalue(), media_type="application/zip",
                        headers={"Content-Disposition": 'attachment; filename="project.zip"'})

    return router
