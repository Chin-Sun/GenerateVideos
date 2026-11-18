import json
import logging
from types import SimpleNamespace as NS
from unittest.mock import MagicMock

import pytest

from drama_bot.contracts import AssetResult, Identity, QualityEvidence, UnsupportedCapability
from drama_bot.media.feishu import (
    FeishuError,
    FeishuEventAdapter,
    FeishuTransport,
    SecretRedactionFilter,
    UnknownDelivery,
)
from drama_bot.media.speech import UnavailableLipSyncProvider, UnavailableSpeechProvider


def identity(chat="chat1"):
    return Identity(tenant_id="tenant", user_id="user", chat_id=chat, message_id="msg")


def test_fixed_target_preview_and_uncertain_send():
    client = MagicMock()
    client.im.v1.message.create.return_value = NS(success=lambda: True, data=NS(message_id="sent"))
    transport = FeishuTransport(
        allowed_tenants={"tenant"},
        allowed_users={"user"},
        client=client,
        allow_unverified_preview=True,
    )
    assert transport.send(identity("chat-A"), "file", "d1") == "sent"
    assert transport.send(identity("chat-B"), "file", "d2") == "sent"
    requests = client.im.v1.message.create.call_args_list
    assert [r.args[0].request_body.receive_id for r in requests] == ["chat-A", "chat-B"]
    transport.send_preview(identity(), "file", "d3")
    disclaimer = client.im.v1.message.create.call_args_list[-2].args[0].request_body
    assert "中文台词/口型质量未验证" in json.loads(disclaimer.content)["text"]
    client.im.v1.message.create.side_effect = TimeoutError("secret")
    with pytest.raises(UnknownDelivery):
        transport.send(identity(), "file", "d4")
    with pytest.raises(FeishuError):
        transport.send(identity().model_copy(update={"user_id": "evil"}), "file", "d5")


def test_synthetic_never_upload(tmp_path):
    client = MagicMock()
    transport = FeishuTransport(
        allowed_tenants=set(), allowed_users=set(), client=client, allow_unverified_preview=True
    )
    asset = AssetResult(
        path=tmp_path / "test.mp4",
        sha256="x",
        duration_seconds=4,
        has_audio=True,
        provenance="synthetic",
        quality=QualityEvidence(synthetic=True),
    )
    with pytest.raises(FeishuError, match="Synthetic"):
        transport.upload(asset)
    client.im.v1.file.create.assert_not_called()


def test_event_allowlist_persistence_and_no_groups():
    persist = MagicMock(return_value="persisted")
    event = NS(
        header=NS(event_id="event1"),
        event=NS(
            sender=NS(tenant_key="tenant", sender_id=NS(open_id="user"), sender_type="user"),
            message=NS(
                message_type="text",
                chat_type="p2p",
                content='{"text":"拍一个短剧"}',
                chat_id="chat",
                message_id="msg",
            ),
        ),
    )
    adapter = FeishuEventAdapter(
        allowed_tenants={"tenant"}, allowed_users={"user"}, persist=persist
    )
    assert adapter.handle_event(event) == "persisted"
    assert persist.call_args.args[1:] == ("event1", "拍一个短剧")
    event.event.message.chat_type = "group"
    assert adapter.handle_event(event) is None
    denied = FeishuEventAdapter(allowed_tenants=set(), allowed_users=set(), persist=persist)
    assert denied.handle_event(event) is None
    assert persist.call_count == 1


def test_official_websocket_entry_and_upload_mock(tmp_path, monkeypatch):
    from drama_bot.media import feishu
    from drama_bot.media.video import ProbeInfo, file_hash

    monkeypatch.setenv("FEISHU_APP_ID", "test-app")
    monkeypatch.setenv("FEISHU_APP_SECRET", "test-secret")
    ws = MagicMock()
    monkeypatch.setattr(feishu.lark.ws, "Client", ws)
    FeishuEventAdapter(allowed_tenants=set(), allowed_users=set(), persist=MagicMock()).start()
    ws.return_value.start.assert_called_once()
    assert ws.call_args.kwargs["event_handler"] is not None
    source = tmp_path / "mock.mp4"
    source.write_bytes(b"MOCK ONLY")
    monkeypatch.setattr(feishu, "probe", lambda _: ProbeInfo(4, True, 160, 90))
    asset = AssetResult(
        path=source,
        sha256=file_hash(source),
        duration_seconds=4,
        has_audio=True,
        provenance="provider",
    )
    client = MagicMock()
    client.im.v1.file.create.return_value = NS(success=lambda: True, data=NS(file_key="file-key"))
    transport = FeishuTransport(
        allowed_tenants={"tenant"},
        allowed_users={"user"},
        client=client,
        allow_unverified_preview=True,
    )
    assert transport.upload(asset) == "file-key"
    body = client.im.v1.file.create.call_args.args[0].request_body
    assert body.file_name == "draft-preview.mp4" and body.duration == 4000


def test_redaction_and_unavailable(monkeypatch):
    monkeypatch.setenv("FEISHU_APP_SECRET", "sensitive")
    record = logging.LogRecord("x", 20, "", 1, "sensitive Bearer token", (), None)
    SecretRedactionFilter().filter(record)
    assert "sensitive" not in record.getMessage() and "token" not in record.getMessage()
    with pytest.raises(UnsupportedCapability):
        UnavailableSpeechProvider().synthesize(None, None)
    with pytest.raises(UnsupportedCapability):
        UnavailableLipSyncProvider().synchronize(None, None, None)
