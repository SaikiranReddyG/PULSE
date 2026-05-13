from __future__ import annotations

from typing import Any

import httpx


def _post_embed(webhook_url: str, embed: dict[str, Any]) -> None:
	response = httpx.post(webhook_url, json={"embeds": [embed]}, timeout=10.0)
	response.raise_for_status()


def send_alert(
	webhook_url: str,
	tier: str,
	title: str,
	description: str,
	fields: dict,
) -> None:
	colors = {
		"critical": 0xFF0000,
		"warning": 0xFFA500,
		"info": 0x0099FF,
	}
	embed = {
		"title": title,
		"description": description,
		"color": colors[tier],
		"fields": [
			{"name": name, "value": str(value), "inline": True}
			for name, value in fields.items()
		],
	}
	_post_embed(webhook_url, embed)


def send_digest(webhook_url: str, sections: list[dict]) -> None:
	embed = {
		"title": "Pulse Digest",
		"color": 0x0099FF,
		"fields": [
			{"name": section["name"], "value": str(section["value"]), "inline": False}
			for section in sections
		],
	}
	_post_embed(webhook_url, embed)
