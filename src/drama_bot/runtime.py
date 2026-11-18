"""Explicit composition root; importing this module performs no external calls."""
import argparse
import json
import os
import time
from pathlib import Path

from sqlalchemy import select

from drama_bot.config import Settings
from drama_bot.contracts import Identity
from drama_bot.core.models import Job
from drama_bot.core.service import CoreService, CreationRequest
from drama_bot.core.worker import Worker
from drama_bot.media.download import SafeDownloader
from drama_bot.media.feishu import FeishuEventAdapter, FeishuTransport
from drama_bot.media.provider import H3Provider
from drama_bot.media.video import FFmpegRenderer, probe


class IntegratedService(CoreService):
    """Reject references before any job is created until publication is implemented."""

    def create_project(self, identity, request, event_id=None):
        if any(s.reference_asset_ids for s in request.shots):
            raise ValueError("capability_blocked: reference publication is not configured")
        return super().create_project(identity, request, event_id)

    def patch_version(self, identity, project_id, request):
        if request.patch.get("reference_asset_ids"):
            raise ValueError("capability_blocked: reference publication is not configured")
        return super().patch_version(identity, project_id, request)


def service_for(settings):
    return IntegratedService(settings.database_url, settings.allowed_user_ids,
                       settings.allowed_tenant_ids, settings.asset_root)


def local_identity(settings):
    if not all((settings.local_tenant_id, settings.local_user_id, settings.local_chat_id)):
        return None
    return Identity(tenant_id=settings.local_tenant_id, user_id=settings.local_user_id,
                    chat_id=settings.local_chat_id, message_id="local-api")


def bridge_credentials(settings):
    # Canonical DRAMA_ configuration overrides legacy adapter aliases, including absent secrets.
    values = {
        "PP_API_KEY": settings.ppapi_api_key,
        "FEISHU_APP_SECRET": settings.feishu_app_secret,
        "FEISHU_VERIFICATION_TOKEN": settings.feishu_verification_token,
        "FEISHU_ENCRYPT_KEY": settings.feishu_encrypt_key,
    }
    for name, value in values.items():
        os.environ[name] = value.get_secret_value() if value else ""
    os.environ["FEISHU_APP_ID"] = settings.feishu_app_id or ""


class UnconfiguredTransport:
    def upload(self, asset):
        raise RuntimeError("Feishu credentials are not configured")

    def send(self, identity, file_key, delivery_id):
        raise RuntimeError("Feishu credentials are not configured")


def build_worker(settings, service=None):
    service = service or service_for(settings)
    bridge_credentials(settings)

    def reservation_exists(job_id):
        # Core reserves exactly once in the same transaction as submission intent.
        # This callback validates that intent, it MUST NOT charge the budget again.
        with service.sessions() as db:
            job = db.scalar(select(Job).where(Job.id == job_id))
            return bool(job and job.state == "submitting" and job.submission_intent
                        and job.lease_token and job.lease_expires_at > service.clock())

    provider = H3Provider(
        base_url=settings.ppapi_base_url,
        downloader=SafeDownloader(root=service.asset_root,
                                  allowed_hosts=set(settings.download_allowed_hosts), probe=probe),
        paid_enabled=settings.paid_calls_enabled,
        authorization_id=settings.paid_authorization_id or "",
        reserve_budget=reservation_exists,
    )
    transport = UnconfiguredTransport()
    if settings.feishu_app_id and settings.feishu_app_secret:
        transport = FeishuTransport(allowed_tenants=set(settings.allowed_tenant_ids),
                                    allowed_users=set(settings.allowed_user_ids),
                                    allow_unverified_preview=settings.allow_unverified_preview)
    return Worker(service, provider, FFmpegRenderer(), transport, settings)


def event_sink(service, settings):
    def persist(identity, event_id, text):
        # No LLM: only an explicit structured creation command is accepted.
        if not text.startswith("/create "):
            return {"error": "structured_command_required"}
        data = json.loads(text[len("/create "):])
        data.setdefault("aspect_ratio", settings.default_aspect_ratio)
        request = CreationRequest.model_validate(data)
        if any(s.reference_asset_ids for s in request.shots):
            raise ValueError("Reference publishing is not configured")
        return service.create_project(identity, request, event_id=event_id)
    return persist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["worker", "ingress", "init-db"])
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    settings = Settings()
    service = service_for(settings)
    if args.mode == "init-db":
        return
    bridge_credentials(settings)
    if args.mode == "ingress":
        FeishuEventAdapter(allowed_tenants=set(settings.allowed_tenant_ids),
                           allowed_users=set(settings.allowed_user_ids),
                           persist=event_sink(service, settings)).start()
        return
    worker = build_worker(settings, service)
    health = Path(settings.asset_root).parent / "worker-heartbeat"
    while True:
        worked = worker.run_once()
        health.write_text(str(time.time()))
        if args.once:
            return
        if not worked:
            time.sleep(1)


if __name__ == "__main__":
    main()
