"""Unit tests for the receiver module."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("PULSE_SQLITE_DB", ":memory:")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "")
os.environ.setdefault("DISCORD_WEBHOOK_URL", "")
os.environ.setdefault("PULSE_RECEIVER_TOKEN", "test-token-123")

from receiver.app import app  # noqa: E402


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def _valid_event(severity: str = "info", source: str = "sentinel") -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "timestamp": "2026-05-01T12:00:00.000+02:00",
        "source": source,
        "source_version": "0.1.0",
        "host": "test-host",
        "event_type": f"{source}.lifecycle.started",
        "severity": severity,
        "payload": {"interface": "lo"},
    }


def _auth_headers(token: str = "test-token-123") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_single_valid_event(client: TestClient) -> None:
    response = client.post("/events", json=_valid_event(), headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 1
    assert body["rejected"] == []


def test_post_array_of_events(client: TestClient) -> None:
    events = [_valid_event(), _valid_event(source="netlab", severity="low")]
    response = client.post("/events", json=events, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 2
    assert body["rejected"] == []


def test_post_rejects_invalid_severity(client: TestClient) -> None:
    response = client.post("/events", json=_valid_event(severity="catastrophic"), headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 0
    assert len(body["rejected"]) == 1


def test_post_rejects_missing_fields(client: TestClient) -> None:
    response = client.post("/events", json={"schema_version": "1.0"}, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 0
    assert len(body["rejected"]) == 1


def test_post_rejects_invalid_json(client: TestClient) -> None:
    response = client.post("/events", content=b"{not json", headers=_auth_headers())
    assert response.status_code == 400


def test_partial_batch_success(client: TestClient) -> None:
    events = [_valid_event(), {"bogus": True}, _valid_event(source="syswatch")]
    response = client.post("/events", json=events, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 2
    assert len(body["rejected"]) == 1


def test_post_events_no_token(client: TestClient) -> None:
    response = client.post("/events", json=_valid_event())
    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}


def test_post_events_wrong_token(client: TestClient) -> None:
    response = client.post("/events", json=_valid_event(), headers=_auth_headers("wrong-token"))
    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}


def test_post_events_correct_token(client: TestClient) -> None:
    response = client.post("/events", json=_valid_event(), headers=_auth_headers("test-token-123"))
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 1
    assert body["rejected"] == []


def test_idempotent_event_accepted_once(client: TestClient) -> None:
    event = {
        "schema_version": "1.0",
        "timestamp": "2026-05-01T12:00:00.000+02:00",
        "source": "sentinel",
        "source_version": "0.1.0",
        "host": "test-host",
        "event_type": "sentinel.lifecycle.started",
        "severity": "info",
        "event_id": "unique-event-123",
        "payload": {"interface": "lo"},
    }
    response1 = client.post("/events", json=event, headers=_auth_headers())
    assert response1.status_code == 200
    assert response1.json()["accepted"] == 1

    response2 = client.post("/events", json=event, headers=_auth_headers())
    assert response2.status_code == 200
    assert response2.json()["accepted"] == 1

    from receiver.app import storage
    cursor = storage._conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_id = ?", ("unique-event-123",)
    )
    assert cursor.fetchone()[0] == 1


def test_event_without_id_not_deduplicated(client: TestClient) -> None:
    event = _valid_event()
    response1 = client.post("/events", json=event, headers=_auth_headers())
    assert response1.status_code == 200
    assert response1.json()["accepted"] == 1

    response2 = client.post("/events", json=event, headers=_auth_headers())
    assert response2.status_code == 200
    assert response2.json()["accepted"] == 1

    from receiver.app import storage
    cursor = storage._conn.execute(
        "SELECT COUNT(*) FROM events WHERE source = ? AND host = ?", ("sentinel", "test-host")
    )
    assert cursor.fetchone()[0] == 2
