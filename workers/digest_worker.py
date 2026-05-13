from __future__ import annotations

import json
import logging
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler

from dashboard.pulse_dashboard.storage import Storage
from workers.discord import send_digest


log = logging.getLogger(__name__)

_RULES_PATH = Path(__file__).resolve().parent.parent / "config" / "alert_rules.yml"
with _RULES_PATH.open("r", encoding="utf-8") as rules_file:
	_RULES_DATA = yaml.safe_load(rules_file)


def _load_storage() -> Storage:
	return Storage(os.environ["PULSE_DB_PATH"])


def _events_last_24_hours(storage: Storage) -> list[dict]:
	cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
	cutoff_iso = cutoff.isoformat()
	with storage._connect() as conn:
		rows = conn.execute(
			"SELECT timestamp, source, event_type, severity, payload_json "
			"FROM events "
			"WHERE datetime(timestamp) >= datetime(?) "
			"ORDER BY datetime(timestamp) ASC, id ASC",
			(cutoff_iso,),
		).fetchall()

	events: list[dict] = []
	for row in rows:
		try:
			payload = json.loads(row["payload_json"])
		except (json.JSONDecodeError, TypeError):
			payload = {}
		events.append(
			{
				"timestamp": row["timestamp"],
				"source": row["source"],
				"event_type": row["event_type"],
				"severity": row["severity"],
				"payload": payload,
			}
		)
	return events


def _numeric_value(payload: dict, preferred_keys: tuple[str, ...]) -> float | None:
	for key in preferred_keys:
		value = payload.get(key)
		if isinstance(value, (int, float)):
			return float(value)
	numeric_values = [float(value) for value in payload.values() if isinstance(value, (int, float))]
	if numeric_values:
		return max(numeric_values)
	return None


def _build_security_section(events: list[dict]) -> dict[str, str]:
	alert_events = [event for event in events if event["source"] == "sentinel" and event["event_type"] == "sentinel.alert"]
	counts = Counter(event["severity"] for event in alert_events)
	lines = [f"Total alerts: {len(alert_events)}"]
	for severity in ("critical", "high", "medium", "low"):
		if severity in counts:
			lines.append(f"{severity}: {counts[severity]}")
	if len(lines) == 1:
		lines.append("No sentinel alerts in the last 24 hours.")
	return {"name": "Security", "value": "\n".join(lines)}


def _build_system_section(events: list[dict]) -> dict[str, str]:
	peaks: dict[str, float] = defaultdict(float)
	for event in events:
		if event["event_type"] not in {
			"system.metrics.cpu",
			"system.metrics.memory",
			"system.metrics.disk",
		}:
			continue
		event_type = event["event_type"]
		payload = event["payload"]
		if event_type == "system.metrics.cpu":
			value = _numeric_value(payload, ("usage_pct", "user_pct", "system_pct", "idle_pct", "core_count"))
			if value is not None:
				peaks["cpu"] = max(peaks["cpu"], value)
		elif event_type == "system.metrics.memory":
			value = _numeric_value(payload, ("mem_used", "mem_available", "mem_free", "mem_total", "swap_used", "swap_free", "swap_total"))
			if value is not None:
				peaks["memory"] = max(peaks["memory"], value)
		elif event_type == "system.metrics.disk":
			disks = payload.get("disks")
			value = None
			if isinstance(disks, list):
				for disk in disks:
					if not isinstance(disk, dict):
						continue
					disk_value = _numeric_value(disk, ("read_bps", "write_bps"))
					if disk_value is not None:
						value = disk_value if value is None else max(value, disk_value)
			if value is None:
				value = _numeric_value(payload, ())
			if value is not None:
				peaks["disk"] = max(peaks["disk"], value)

	lines = []
	for metric in ("cpu", "memory", "disk"):
		peak = peaks.get(metric)
		if peak is None:
			lines.append(f"{metric}: no data")
		else:
			lines.append(f"{metric}: peak {peak:.2f}")
	return {"name": "System", "value": "\n".join(lines)}


def _build_activity_section(events: list[dict]) -> dict[str, str]:
	lifecycle = Counter()
	source_counts = Counter()
	last_seen: dict[str, str] = {}
	for event in events:
		source = event["source"]
		source_counts[source] += 1
		last_seen[source] = event["timestamp"]
		if event["event_type"] in {"sentinel.lifecycle.started", "sentinel.lifecycle.stopped"}:
			lifecycle[event["event_type"].rsplit(".", 1)[-1]] += 1

	lines = [
		f"started: {lifecycle.get('started', 0)}",
		f"stopped: {lifecycle.get('stopped', 0)}",
	]
	for source in sorted(source_counts):
		lines.append(f"{source}: {source_counts[source]} events, last seen {last_seen[source]}")
	if len(source_counts) == 0:
		lines.append("No activity in the last 24 hours.")
	return {"name": "Activity", "value": "\n".join(lines)}


def run_digest() -> None:
	storage = _load_storage()
	events = _events_last_24_hours(storage)
	sections = [
		_build_security_section(events),
		_build_system_section(events),
		_build_activity_section(events),
	]
	send_digest(os.environ["PULSE_DISCORD_WEBHOOK"], sections)


def main() -> None:
	send_time = _RULES_DATA["digest"]["send_time"]
	hour_str, minute_str = send_time.split(":", 1)
	scheduler = BlockingScheduler(timezone="UTC")
	scheduler.add_job(run_digest, "cron", hour=int(hour_str), minute=int(minute_str))
	scheduler.start()


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	main()
