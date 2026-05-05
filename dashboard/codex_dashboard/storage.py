"""Read-only SQLite query layer for the codex dashboard.

All queries open the database in ?mode=ro to guarantee the dashboard
cannot accidentally write. WAL mode set by the receiver allows concurrent
reads without blocking writes.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class Event:
    id: int
    timestamp: datetime
    source: str
    event_type: str
    severity: str
    payload: dict


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def is_available(self) -> bool:
        """Check if the database file exists and is readable."""
        return Path(self.db_path).exists()

    def total_events(self) -> int:
        """Return total count of events in the database."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM events")
                return cursor.fetchone()[0]
        except Exception:
            return 0

    def events_in_window(self, minutes: int) -> int:
        """Return count of events in the last N minutes."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                cursor = conn.cursor()
                cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
                cursor.execute(
                    "SELECT COUNT(*) FROM events WHERE timestamp > ?",
                    (cutoff.isoformat(),),
                )
                return cursor.fetchone()[0]
        except Exception:
            return 0

    def severity_counts(self, minutes: int) -> dict[str, int]:
        """Return event counts by severity for the last N minutes."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                cursor = conn.cursor()
                cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
                cursor.execute(
                    "SELECT severity, COUNT(*) FROM events WHERE timestamp > ? GROUP BY severity",
                    (cutoff.isoformat(),),
                )
                return dict(cursor.fetchall())
        except Exception:
            return {}

    def source_counts(self, minutes: int) -> dict[str, int]:
        """Return event counts by source for the last N minutes."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                cursor = conn.cursor()
                cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
                cursor.execute(
                    "SELECT source, COUNT(*) FROM events WHERE timestamp > ? GROUP BY source",
                    (cutoff.isoformat(),),
                )
                return dict(cursor.fetchall())
        except Exception:
            return {}

    def recent_events(
        self, limit: int = 50, source: str | None = None
    ) -> list[Event]:
        """Return the most recent events."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if source:
                    cursor.execute(
                        "SELECT * FROM events WHERE source = ? ORDER BY id DESC LIMIT ?",
                        (source, limit),
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
                    )
                return [
                    Event(
                        id=row["id"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        source=row["source"],
                        event_type=row["event_type"],
                        severity=row["severity"],
                        payload=json.loads(row["payload_json"]),
                    )
                    for row in cursor.fetchall()
                ]
        except Exception:
            return []

    def syswatch_latest_metrics(self) -> dict:
        """Return the latest syswatch.metrics event payload."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT payload_json FROM events WHERE source = 'syswatch' AND event_type = 'syswatch.metrics' ORDER BY id DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row["payload_json"])
                return {}
        except Exception:
            return {}

    def sentinel_alert_counts_by_detector(self, minutes: int) -> dict[str, int]:
        """Return sentinel alert counts grouped by detection_type."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                cursor = conn.cursor()
                cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
                cursor.execute(
                    """
                    SELECT json_extract(payload_json, '$.detection_type') as detector, COUNT(*)
                    FROM events
                    WHERE source = 'sentinel' AND event_type = 'sentinel.alert' AND timestamp > ?
                    GROUP BY detector
                    """,
                    (cutoff.isoformat(),),
                )
                return dict(cursor.fetchall())
        except Exception:
            return {}

    def netlab_recent_scenarios(self, limit: int = 10) -> list[dict]:
        """Return recent netlab scenario events."""
        try:
            with sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, timestamp, payload_json FROM events WHERE source = 'netlab' ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
                scenarios = []
                for row in cursor.fetchall():
                    payload = json.loads(row["payload_json"])
                    scenarios.append(
                        {
                            "id": row["id"],
                            "timestamp": row["timestamp"],
                            "scenario": payload.get("scenario", "unknown"),
                        }
                    )
                return scenarios
        except Exception:
            return []
