"""WhatsApp ingest-only event transport tests.

Validates the generic agentDispatchAllowed=False flow: unauthorized bot-mode
messages reach pre_gateway_dispatch plugins for observe-only ingestion, then drop
fail-closed instead of reaching normal agent dispatch.
"""

import asyncio

from gateway.config import PlatformConfig
from plugins.platforms.whatsapp.adapter import WhatsAppAdapter


def _adapter() -> WhatsAppAdapter:
    return WhatsAppAdapter(
        PlatformConfig(
            enabled=True,
            extra={
                "dm_policy": "allowlist",
                "allow_from": ["allowed@s.whatsapp.net"],
            },
        )
    )


def _unauthorized_message(**overrides):
    data = {
        "messageId": "msg-1",
        "chatId": "unauthorized@s.whatsapp.net",
        "senderId": "unauthorized@s.whatsapp.net",
        "senderName": "Unknown Sender",
        "chatName": "Unknown Sender",
        "isGroup": False,
        "body": "business lead",
        "hasMedia": False,
        "mediaUrls": [],
    }
    data.update(overrides)
    return data


def test_regular_unauthorized_whatsapp_dm_is_rejected_by_adapter_policy():
    adapter = _adapter()
    event = asyncio.run(adapter._build_message_event(_unauthorized_message()))
    assert event is None


def test_ingest_only_unauthorized_whatsapp_dm_reaches_plugin_hook_then_drops(monkeypatch):
    adapter = _adapter()
    data = _unauthorized_message(
        agentDispatchAllowed=False,
        ingestReason="allowlist_mismatch",
    )

    event = asyncio.run(adapter._build_message_event(data))
    assert event is not None
    assert event.text == "business lead"
    assert event.raw_message["agentDispatchAllowed"] is False

    calls = []

    def fake_invoke_hook(name, **kwargs):
        calls.append((name, kwargs))
        return [{"action": "skip"}]

    monkeypatch.setattr("hermes_cli.plugins.invoke_hook", fake_invoke_hook)
    asyncio.run(adapter._handle_ingest_only_event(event))

    assert len(calls) == 1
    name, payload = calls[0]
    assert name == "pre_gateway_dispatch"
    assert payload["event"] is event
