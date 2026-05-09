"""SQLite + Redis Streams persistence layer."""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any

import redis

log = logging.getLogger("receiver.storage")

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

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
""".strip()


class Storage:
    def __init__(self, sqlite_path: str, redis_host: str, redis_port: int, redis_password: str | None):
        self.sqlite_path = sqlite_path
        self.redis_host = redis_host
        self.redis_port = redis_port
        self._conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._conn.execute("PRAGMA synchronous = NORMAL")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()
        self._redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_timeout=2.0,
        )
        try:
            self._redis.ping()
            log.info("redis connected")
        except Exception as exc:
            log.warning("redis ping failed (will continue without redis): %s", exc)
            self._redis = None

    def write_event(self, event: dict[str, Any], received_at: str) -> None:
        self._write_sqlite(event, received_at)
        self._write_redis_stream(event)

    def _write_sqlite(self, event: dict[str, Any], received_at: str) -> None:
        self._conn.execute(
            """INSERT INTO events
               (received_at, timestamp, schema_version, source, source_version,
                host, event_type, severity, payload_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                received_at,
                event["timestamp"],
                event["schema_version"],
                event["source"],
                event.get("source_version"),
                event.get("host"),
                event["event_type"],
                event["severity"],
                json.dumps(event.get("payload", {})),
            ),
        )
        self._conn.commit()

    def _write_redis_stream(self, event: dict[str, Any]) -> None:
        if self._redis is None:
            return
        try:
            stream_key = f"pulse:events:{event['source']}"
            self._redis.xadd(
                stream_key,
                {"data": json.dumps(event)},
                maxlen=10000,
                approximate=True,
            )
        except Exception as exc:
            log.warning("redis xadd failed: %s", exc)

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

        if self._redis is not None:
            try:
                self._redis.close()
            except Exception:
                pass