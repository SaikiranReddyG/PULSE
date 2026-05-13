"""Read-only SQLite query layer for the pulse dashboard.

All queries open the database in ?mode=ro to guarantee the dashboard
cannot accidentally write. WAL mode set by the receiver allows concurrent
reads without blocking writes.
"""

from __future__ import annotations

import ipaddress
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class Event:
    id: int
    timestamp: str
    source: str
    event_type: str
    severity: str
    payload: dict


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._uri = f"file:{db_path}?mode=ro"
        self._trusted_networks = self._load_trusted_networks()

    @staticmethod
    def _load_trusted_networks() -> list:
        raw = os.environ.get("PULSE_TRUSTED_NETWORKS", "")
        networks = []
        for cidr in raw.split(","):
            cidr = cidr.strip()
            if cidr:
                networks.append(ipaddress.ip_network(cidr, strict=False))
        return networks

    def is_trusted_src_ip(self, src_ip: str | None) -> bool:
        if not src_ip:
            return False
        try:
            address = ipaddress.ip_address(src_ip)
        except ValueError:
            return False
        return any(address in network for network in self._trusted_networks)

    def _connect(self) -> sqlite3.Connection:
        # Re-open per call. SQLite connections are cheap; avoids stale handles.
        conn = sqlite3.connect(self._uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def is_available(self) -> bool:
        if not Path(self.db_path).is_file():
            return False
        try:
            with self._connect() as conn:
                conn.execute("SELECT 1 FROM events LIMIT 1")
            return True
        except sqlite3.Error:
            return False

    def total_events(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()
            return row["n"]

    def events_in_window(self, minutes: int) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=minutes))
        cutoff_iso = cutoff.isoformat()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM events "
                "WHERE datetime(timestamp) >= datetime(?)",
                (cutoff_iso,),
            ).fetchone()
            return row["n"]

    def severity_counts(self, minutes: int = 60) -> dict[str, int]:
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=minutes))
        cutoff_iso = cutoff.isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT severity, COUNT(*) AS n FROM events "
                "WHERE datetime(timestamp) >= datetime(?) "
                "GROUP BY severity",
                (cutoff_iso,),
            ).fetchall()
            return {r["severity"]: r["n"] for r in rows}

    def source_counts(self, minutes: int = 60) -> dict[str, int]:
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=minutes))
        cutoff_iso = cutoff.isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT source, COUNT(*) AS n FROM events "
                "WHERE datetime(timestamp) >= datetime(?) "
                "GROUP BY source",
                (cutoff_iso,),
            ).fetchall()
            return {r["source"]: r["n"] for r in rows}

    def last_seen_by_source(self) -> dict[str, str | None]:
        last_seen: dict[str, str | None] = {"sentinel": None, "syswatch": None, "netlab": None}
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT source, MAX(timestamp) AS ts FROM events "
                "WHERE source IN ('sentinel','syswatch','netlab') "
                "GROUP BY source",
            ).fetchall()
        for row in rows:
            last_seen[row["source"]] = row["ts"]
        return last_seen

    def recent_events(self, limit: int = 50, source: str | None = None, exclude_routine: bool = False) -> list[Event]:
        sql = ("SELECT id, timestamp, source, event_type, severity, payload_json "
               "FROM events ")
        params: list = []
        conditions = []
        if source:
            conditions.append("source = ?")
            params.append(source)
        if exclude_routine:
            conditions.append("NOT (source = 'syswatch' AND (event_type LIKE 'syswatch.metrics.%' OR event_type LIKE 'system.metrics.%' OR event_type = 'syswatch.internal'))")
        
        if conditions:
            sql += "WHERE " + " AND ".join(conditions) + " "
        
        sql += "ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        events: list[Event] = []
        for r in rows:
            try:
                payload = json.loads(r["payload_json"])
            except (json.JSONDecodeError, TypeError):
                payload = {}
            events.append(Event(
                id=r["id"],
                timestamp=r["timestamp"],
                source=r["source"],
                event_type=r["event_type"],
                severity=r["severity"],
                payload=payload,
            ))
        return events

    def events_per_minute(self, minutes: int = 60) -> list[tuple[str, int]]:
        """Return list of (minute_iso, count) covering the last N minutes."""
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=minutes))
        cutoff_iso = cutoff.isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT strftime('%Y-%m-%dT%H:%M:00Z', timestamp) AS minute, "
                "       COUNT(*) AS n "
                "FROM events "
                "WHERE datetime(timestamp) >= datetime(?) "
                "  AND NOT (source = 'syswatch' AND (event_type LIKE 'syswatch.metrics.%' OR event_type LIKE 'system.metrics.%' OR event_type = 'syswatch.internal')) "
                "GROUP BY minute "
                "ORDER BY minute",
                (cutoff_iso,),
            ).fetchall()
            return [(r["minute"], r["n"]) for r in rows]

    def latest_event_by_type(self, source: str, event_type_prefix: str) -> Event | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, timestamp, source, event_type, severity, payload_json "
                "FROM events "
                "WHERE source = ? AND event_type LIKE ? "
                "ORDER BY id DESC LIMIT 1",
                (source, event_type_prefix + "%"),
            ).fetchone()
        if not row:
            return None
        try:
            payload = json.loads(row["payload_json"])
        except (json.JSONDecodeError, TypeError):
            payload = {}
        return Event(
            id=row["id"], timestamp=row["timestamp"], source=row["source"],
            event_type=row["event_type"], severity=row["severity"], payload=payload,
        )

    def syswatch_latest_metrics(self) -> dict[str, Event | None]:
        def latest_for_prefixes(metric_name: str) -> Event | None:
            newest: Event | None = None
            for prefix in (f"syswatch.metrics.{metric_name}", f"system.metrics.{metric_name}"):
                event = self.latest_event_by_type("syswatch", prefix)
                if event and (newest is None or event.id > newest.id):
                    newest = event
            return newest

        return {
            "cpu": latest_for_prefixes("cpu"),
            "memory": latest_for_prefixes("memory"),
            "disk": latest_for_prefixes("disk"),
            "network": latest_for_prefixes("network"),
        }

    def syswatch_recent_signals(self, limit: int = 10) -> list[Event]:
        sql = (
            "SELECT id, timestamp, source, event_type, severity, payload_json "
            "FROM events "
            "WHERE source = 'syswatch' "
            "  AND ("
            "event_type LIKE 'syswatch.anomaly%' OR event_type LIKE 'system.anomaly%' OR "
            "event_type LIKE 'syswatch.lifecycle%' OR event_type LIKE 'system.lifecycle%'"
            ") "
            "ORDER BY id DESC LIMIT ?"
        )
        with self._connect() as conn:
            rows = conn.execute(sql, (limit,)).fetchall()
        
        events: list[Event] = []
        for r in rows:
            try:
                payload = json.loads(r["payload_json"])
            except (json.JSONDecodeError, TypeError):
                payload = {}
            events.append(Event(
                id=r["id"],
                timestamp=r["timestamp"],
                source=r["source"],
                event_type=r["event_type"],
                severity=r["severity"],
                payload=payload,
            ))
        return events

    def sentinel_alert_counts_by_detector(self, minutes: int = 60) -> dict[str, int]:
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=minutes))
        cutoff_iso = cutoff.isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT json_extract(payload_json, '$.detection_type') AS det, "
                "       COUNT(*) AS n "
                "FROM events "
                "WHERE source = 'sentinel' AND event_type = 'sentinel.alert' "
                "  AND datetime(timestamp) >= datetime(?) "
                "GROUP BY det",
                (cutoff_iso,),
            ).fetchall()
            return {(r["det"] or "unknown"): r["n"] for r in rows}

    def sentinel_top_talkers(self, hours: int = 24, limit: int = 10) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT json_extract(payload_json, '$.src_ip') AS src_ip, "
                "       COUNT(*) AS alert_count, "
                "       MAX(timestamp) AS last_seen "
                "FROM events "
                "WHERE source = 'sentinel' "
                "  AND event_type = 'sentinel.alert' "
                "  AND datetime(timestamp) >= datetime('now', ?) "
                "  AND json_extract(payload_json, '$.src_ip') IS NOT NULL "
                "GROUP BY src_ip "
                "ORDER BY alert_count DESC "
                "LIMIT ?",
                (f"-{hours} hours", limit),
            ).fetchall()
        return [
            {
                "src_ip": r["src_ip"],
                "alert_count": r["alert_count"],
                "last_seen": r["last_seen"],
            }
            for r in rows
        ]

    def netlab_recent_scenarios(self, limit: int = 10) -> list[dict]:
        """Return one row per scenario.started, with completed/aborted status if found."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, event_type, severity, payload_json "
                "FROM events "
                "WHERE source = 'netlab' "
                "  AND event_type IN ('netlab.scenario.started', 'netlab.scenario.completed', 'netlab.scenario.aborted') "
                "ORDER BY id DESC "
                "LIMIT ?",
                (limit * 3,),  # over-fetch since we collapse pairs
            ).fetchall()

        # Build per-scenario_name list of (id, event_type, timestamp)
        by_name: dict[str, list] = {}
        for r in rows:
            try:
                payload = json.loads(r["payload_json"])
            except (json.JSONDecodeError, TypeError):
                payload = {}
            name = payload.get("scenario", "unknown")
            by_name.setdefault(name, []).append((r["id"], r["event_type"], r["timestamp"]))

        scenarios: list[dict] = []
        for name, entries in by_name.items():
            # entries are already in DESC id order from the SQL ORDER BY
            started = next((e for e in entries if e[1] == "netlab.scenario.started"), None)
            if not started:
                continue
            completed = any(e[0] > started[0] and e[1] == "netlab.scenario.completed" for e in entries)
            aborted = any(e[0] > started[0] and e[1] == "netlab.scenario.aborted" for e in entries)
            status = "completed" if completed else ("aborted" if aborted else "running")
            scenarios.append({
                "scenario": name,
                "started_at": started[2],
                "status": status,
            })
        # Sort by most recent start
        scenarios.sort(key=lambda s: s["started_at"], reverse=True)
        return scenarios[:limit]
