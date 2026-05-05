"""Pytest fixtures for codex-dashboard."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from codex_dashboard.storage import Storage


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at     TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    source          TEXT NOT NULL,
    source_version  TEXT,
    host            TEXT,
    event_type      TEXT NOT NULL,
    severity        TEXT NOT NULL,
    payload_json    TEXT NOT NULL
);
"""


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.db"
    conn = sqlite3.connect(str(db))
    conn.executescript(SCHEMA_SQL)
    now_iso = datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")
    rows = [
        ("sentinel", "sentinel.lifecycle.started", "info", {"interface": "lo"}),
        ("sentinel", "sentinel.alert", "high", {"detection_type": "PORT_SCAN", "src_ip": "1.2.3.4", "dst_ip": "5.6.7.8", "message": "test"}),
        ("netlab", "netlab.scenario.started", "info", {"scenario": "arp_spoof"}),
        ("netlab", "netlab.scenario.completed", "info", {"scenario": "arp_spoof", "duration_seconds": 12.0}),
        ("syswatch", "syswatch.metrics.cpu", "info", {"usage_pct": 7.7, "user_pct": 4.7, "system_pct": 2.0, "idle_pct": 92.3, "core_count": 12}),
        ("syswatch", "syswatch.metrics.memory", "info", {"mem_total": 16000000, "mem_used": 9000000, "mem_available": 7000000, "swap_total": 0, "swap_used": 0}),
    ]
    for source, event_type, severity, payload in rows:
        conn.execute(
            "INSERT INTO events (received_at, timestamp, schema_version, source, source_version, host, event_type, severity, payload_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (now_iso, now_iso, "1.0", source, "0.1.0", "test-host", event_type, severity, json.dumps(payload)),
        )
    conn.commit()
    conn.close()
    return db


@pytest.fixture
def storage(temp_db: Path) -> Storage:
    return Storage(str(temp_db))
