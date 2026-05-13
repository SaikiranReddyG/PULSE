"""Discord webhook alerting."""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

log = logging.getLogger("receiver.alerting")

_SEVERITY_COLOR = {
    "high": 0xE67E22,
    "critical": 0xE74C3C,
}


def maybe_alert_discord(event: dict[str, Any]) -> None:
    """Fire a Discord webhook for high/critical events. No-op if not configured."""
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook:
        return

    payload = {
        "embeds": [
            {
                "title": f"[{event['severity'].upper()}] {event['event_type']}",
                "description": _format_description(event),
                "color": _SEVERITY_COLOR.get(event["severity"], 0x95A5A6),
                "footer": {
                    "text": f"source: {event['source']} · host: {event.get('host', 'unknown')}"
                },
                "timestamp": event["timestamp"],
            }
        ]
    }
    try:
        response = requests.post(webhook, json=payload, timeout=5)
        if response.status_code >= 300:
            log.warning("discord webhook returned %s: %s", response.status_code, response.text[:200])
    except Exception as exc:
        log.warning("discord webhook failed: %s", exc)


def _format_description(event: dict[str, Any]) -> str:
    payload = event.get("payload", {})
    lines = []
    for key, value in list(payload.items())[:8]:
        lines.append(f"**{key}**: `{value}`")
    return "\n".join(lines) if lines else "_(no payload)_"