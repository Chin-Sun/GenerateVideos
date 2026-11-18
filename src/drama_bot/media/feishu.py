"""Official SDK transport: fixed identities, environment secrets, no message logging."""

import json
import logging
import os
import re
from collections.abc import Callable

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateFileRequest,
    CreateFileRequestBody,
    CreateMessageRequest,
    CreateMessageRequestBody,
)

from drama_bot.contracts import AssetResult, Identity
from drama_bot.media.video import file_hash, probe


class FeishuError(RuntimeError):
    pass


class UnknownDelivery(FeishuError):
    """Send may have succeeded: stop and reconcile; do not automatically resend."""


class SecretRedactionFilter(logging.Filter):
    def filter(self, record):
        text = record.getMessage()
        for key in (
            "PP_API_KEY",
            "FEISHU_APP_SECRET",
            "FEISHU_VERIFICATION_TOKEN",
            "FEISHU_ENCRYPT_KEY",
        ):
            value = os.environ.get(key)
            if value:
                text = text.replace(value, "[REDACTED]")
        text = re.sub(r"(?i)Bearer\s+[^\s,;]+", "Bearer [REDACTED]", text)
        record.msg, record.args = text, ()
        # Exception chains from vendor HTTP libraries can include headers/URLs.
        record.exc_info = None
        record.exc_text = None
        return True


def install_redaction():
    for name in ("", "Lark", "lark_oapi", "httpx", "httpcore"):
        logger = logging.getLogger(name)
        logger.addFilter(SecretRedactionFilter())
        for handler in logger.handlers:
            handler.addFilter(SecretRedactionFilter())


def _credentials():
    app_id, secret = os.environ.get("FEISHU_APP_ID"), os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not secret:
        raise FeishuError("Feishu environment credentials required")
    return app_id, secret


class FeishuEventAdapter:
    """Callback persists before returning. persist(identity,event_id,text) must deduplicate.

    Only the authenticated official websocket dispatcher should call handle_event.
    This is not an unauthenticated HTTP webhook handler.
    """

    def __init__(
        self,
        *,
        allowed_tenants: set[str],
        allowed_users: set[str],
        persist: Callable[[Identity, str, str], object],
    ):
        self.allowed_tenants = allowed_tenants
        self.allowed_users = allowed_users
        self.persist = persist

    def handle_event(self, data):
        event = data.event
        sender = event.sender
        message = event.message
        tenant = sender.tenant_key
        user = sender.sender_id.open_id
        if tenant not in self.allowed_tenants or user not in self.allowed_users:
            return None
        if sender.sender_type != "user" or message.message_type != "text":
            return None
        # MVP is personal chat only, so group text cannot trigger paid generation.
        if message.chat_type != "p2p":
            return None
        try:
            text = json.loads(message.content)["text"]
        except (ValueError, KeyError, TypeError):
            return None
        if not isinstance(text, str) or not text.strip() or len(text) > 10000:
            return None
        identity = Identity(
            tenant_id=tenant, user_id=user, chat_id=message.chat_id, message_id=message.message_id
        )
        return self.persist(identity, data.header.event_id, text)

    def start(self):
        """Blocking official long connection; launch as dedicated ingress process."""
        install_redaction()
        app_id, secret = _credentials()
        dispatcher = (
            lark.EventDispatcherHandler.builder(
                os.environ.get("FEISHU_ENCRYPT_KEY", ""),
                os.environ.get("FEISHU_VERIFICATION_TOKEN", ""),
            )
            .register_p2_im_message_receive_v1(self.handle_event)
            .build()
        )
        client = lark.ws.Client(
            app_id, secret, event_handler=dispatcher, log_level=lark.LogLevel.ERROR
        )
        client.start()


class FeishuTransport:
    def __init__(
        self,
        *,
        allowed_tenants: set[str],
        allowed_users: set[str],
        client=None,
        allow_unverified_preview: bool = False,
    ):
        install_redaction()
        self.allowed_tenants = allowed_tenants
        self.allowed_users = allowed_users
        self.allow_unverified_preview = allow_unverified_preview
        if client is None:
            app_id, secret = _credentials()
            client = (
                lark.Client.builder()
                .app_id(app_id)
                .app_secret(secret)
                .log_level(lark.LogLevel.ERROR)
                .build()
            )
        self.client = client

    def upload(self, asset: AssetResult) -> str:
        if asset.provenance == "synthetic" or asset.quality.synthetic:
            raise FeishuError("Synthetic fixtures must never be uploaded to users")
        if not asset.quality.approved and not self.allow_unverified_preview:
            raise FeishuError("Unreviewed asset requires explicit draft preview transport")
        if file_hash(asset.path) != asset.sha256 or not asset.has_audio:
            raise FeishuError("Invalid asset integrity/audio")
        info = probe(asset.path)
        if not info.has_audio:
            raise FeishuError("Missing dialogue audio")
        with asset.path.open("rb") as f:
            body = (
                CreateFileRequestBody.builder()
                .file_type("mp4")
                .file_name("draft-preview.mp4" if not asset.quality.approved else "drama.mp4")
                .duration(round(info.duration_seconds * 1000))
                .file(f)
                .build()
            )
            request = CreateFileRequest.builder().request_body(body).build()
            try:
                response = self.client.im.v1.file.create(request)
            except Exception:  # noqa: BLE001 - external SDK boundary; redact and classify ambiguity
                raise FeishuError("Feishu upload failed") from None
        if not response.success() or not response.data or not response.data.file_key:
            raise FeishuError("Feishu upload rejected")
        return response.data.file_key

    def send_preview(self, identity: Identity, file_key: str, delivery_id: str) -> str:
        if not self.allow_unverified_preview:
            raise FeishuError("Draft preview transport not enabled")
        # Both upload filename and a preceding text message explicitly mark the draft.
        return self._send(identity, file_key, delivery_id, preview=True)

    def send(self, identity: Identity, file_key: str, delivery_id: str) -> str:
        return self._send(identity, file_key, delivery_id, preview=False)

    def _send(self, identity: Identity, file_key: str, delivery_id: str, *, preview: bool) -> str:
        if (
            identity.tenant_id not in self.allowed_tenants
            or identity.user_id not in self.allowed_users
        ):
            raise FeishuError("Recipient not allowlisted")
        if not file_key or not delivery_id:
            raise FeishuError("Missing delivery key")
        if preview:
            notice_body = (
                CreateMessageRequestBody.builder()
                .receive_id(identity.chat_id)
                .msg_type("text")
                .content(
                    json.dumps({"text": "草稿预览，中文台词/口型质量未验证"}, ensure_ascii=False)
                )
                .build()
            )
            notice = (
                CreateMessageRequest.builder()
                .receive_id_type("chat_id")
                .request_body(notice_body)
                .build()
            )
            try:
                result = self.client.im.v1.message.create(notice)
                if not result.success():
                    raise UnknownDelivery("Preview disclaimer delivery not confirmed")
            except Exception:  # noqa: BLE001 - external SDK boundary; redact and classify ambiguity
                raise UnknownDelivery("Preview disclaimer outcome unknown") from None
        # File message works without an invented thumbnail/image_key. Core persists delivery ID.
        body = (
            CreateMessageRequestBody.builder()
            .receive_id(identity.chat_id)
            .msg_type("file")
            .content(json.dumps({"file_key": file_key}))
            .build()
        )
        request = (
            CreateMessageRequest.builder().receive_id_type("chat_id").request_body(body).build()
        )
        try:
            response = self.client.im.v1.message.create(request)
        except Exception:  # noqa: BLE001 - external SDK boundary; redact and classify ambiguity
            raise UnknownDelivery("Feishu send outcome unknown") from None
        if not response.success():
            # SDK codes do not establish absence of side effects; conservative reconciliation.
            raise UnknownDelivery("Feishu send not confirmed")
        if not response.data or not response.data.message_id:
            raise UnknownDelivery("Feishu response lacks message ID")
        return response.data.message_id
