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
    timestamp       TEXT NOT NULL,
    source          TEXT NOT NULL,
    source_version  TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    severity        TEXT NOT NULL,
    payload_json    TEXT NOT NULL
);
"""


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Create an in-memory SQLite database with sample data."""
    db = tmp_path / "test.db"

    conn = sqlite3.connect(str(db))
    conn.execute(SCHEMA_SQL)

    # Insert sample events
    events = [
        (
            "2026-05-05T10:00:00.000+0000",
            "sentinel",
            "0.1.0",
            "sentinel.lifecycle.started",
            "info",
            json.dumps({"interface": "eth0"}),
        ),
        (
            "2026-05-05T10:01:00.000+0000",
            "sentinel",
            "0.1.0",
            "sentinel.alert",
            "high",
            json.dumps({"detection_type": "PORT_SCAN", "src_ip": "1.2.3.4"}),
        ),
        (
            "2026-05-05T10:02:00.000+0000",
            "netlab",
            "0.1.0",
            "netlab.scenario.started",
            "info",
            json.dumps({"scenario": "arp_spoof"}),
        ),
        (
            "2026-05-05T10:03:00.000+0000",
            "syswatch",
            "0.1.0",
            "syswatch.metrics",
            "info",
            json.dumps({"cpu_percent": 42.5, "mem_percent": 61.0}),
        ),
        (
            "2026-05-05T10:04:00.000+0000",
            "syswatch",
            "0.1.0",
            "syswatch.metrics",
            "info",
            json.dumps({"cpu_percent": 45.0, "mem_percent": 62.0}),
        ),
        (
            "2026-05-05T10:05:00.000+0000",
            "sentinel",
            "0.1.0",
            "sentinel.alert",
            "critical",
            json.dumps({"detection_type": "DDoS", "src_ip": "10.0.0.1"}),
        ),
    ]

    for event in events:
        conn.execute(
            """
            INSERT INTO events (timestamp, source, source_version, event_type, severity, payload_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            event,
        )

    conn.commit()
    conn.close()

    return db


@pytest.fixture
def storage(temp_db: Path) -> Storage:
    """Create a Storage instance pointing to the test database."""
    return Storage(str(temp_db))
