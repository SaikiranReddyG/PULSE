from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from typing import Any

import redis

from workers.discord import send_alert
from workers.rules import rules


log = logging.getLogger(__name__)


def _redis_client() -> redis.Redis:
	return redis.Redis(
		host=os.environ.get("REDIS_HOST", "localhost"),
		port=int(os.environ.get("REDIS_PORT", "6379")),
		password=os.environ.get("REDIS_PASSWORD"),
		decode_responses=True,
	)


def _summarize_event(event: dict[str, Any]) -> str:
	lines = [f"source: {event.get('source', 'unknown')}", f"timestamp: {event.get('timestamp', 'unknown')}"]
	payload = event.get("payload")
	if isinstance(payload, dict):
		for key, value in list(payload.items())[:3]:
			lines.append(f"{key}: {value}")
	else:
		extra_keys = [key for key in event.keys() if key not in {"source", "timestamp", "event_type", "severity", "payload"}]
		for key in extra_keys[:3]:
			lines.append(f"{key}: {event.get(key)}")
	return "\n".join(lines)


def main() -> None:
	webhook_url = os.environ["PULSE_DISCORD_WEBHOOK"]
	last_fired: dict[str, datetime | None] = {}

	while True:
		try:
			client = _redis_client()
			stream_key = "pulse:events:sentinel"
			last_id = "$"

			while True:
				records = client.xread({stream_key: last_id}, block=5000, count=1)
				if not records:
					continue

				for _, messages in records:
					for message_id, fields in messages:
						last_id = message_id
						raw_data = fields.get("data")
						if raw_data is None:
							continue

						try:
							event = json.loads(raw_data)
						except json.JSONDecodeError:
							log.exception("invalid event payload from redis stream")
							continue

						event_type = event.get("event_type")
						severity = event.get("severity")
						if not isinstance(event_type, str) or not isinstance(severity, str):
							continue

						tier = rules.tier_for_sentinel_alert(severity)
						if tier is None:
							continue

						now = datetime.utcnow()
						if rules.should_throttle(tier, last_fired.get(tier)):
							continue

						try:
							send_alert(
								webhook_url=webhook_url,
								tier=tier,
								title=event_type,
								description=_summarize_event(event),
								fields={"severity": severity, "source": "sentinel"},
							)
						except Exception:
							log.exception("discord webhook failed for tier %s", tier)
							continue

						last_fired[tier] = now
		except redis.RedisError:
			log.exception("redis connection failed; retrying in 10 seconds")
			time.sleep(10)


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	main()
