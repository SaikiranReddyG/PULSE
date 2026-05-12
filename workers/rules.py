from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import yaml


_RULES_PATH = Path(__file__).resolve().parent.parent / "config" / "alert_rules.yml"
with _RULES_PATH.open("r", encoding="utf-8") as rules_file:
	_RULES_DATA = yaml.safe_load(rules_file)


class AlertRules:
	def __init__(self) -> None:
		self._data = _RULES_DATA

	def tier_for_sentinel_alert(self, severity: str) -> str | None:
		if severity in {"critical", "high"}:
			return "critical"
		if severity == "medium":
			return "warning"
		if severity == "low":
			return "info"
		return None

	def should_throttle(self, tier: str, last_fired: datetime | None) -> bool:
		if tier == "critical":
			return False
		if tier == "info":
			return True
		if tier != "warning" or last_fired is None:
			return False
		cooldown_minutes = self._data["throttle"]["warning_cooldown_minutes"]
		return datetime.utcnow() - last_fired < timedelta(minutes=cooldown_minutes)


rules = AlertRules()
