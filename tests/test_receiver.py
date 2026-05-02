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

os.environ.setdefault("CODEX_SQLITE_DB", ":memory:")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "")
os.environ.setdefault("DISCORD_WEBHOOK_URL", "")

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


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_single_valid_event(client: TestClient) -> None:
    response = client.post("/events", json=_valid_event())
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 1
    assert body["rejected"] == []


def test_post_array_of_events(client: TestClient) -> None:
    events = [_valid_event(), _valid_event(source="netlab", severity="low")]
    response = client.post("/events", json=events)
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 2
    assert body["rejected"] == []


def test_post_rejects_invalid_severity(client: TestClient) -> None:
    response = client.post("/events", json=_valid_event(severity="catastrophic"))
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 0
    assert len(body["rejected"]) == 1


def test_post_rejects_missing_fields(client: TestClient) -> None:
    response = client.post("/events", json={"schema_version": "1.0"})
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 0
    assert len(body["rejected"]) == 1


def test_post_rejects_invalid_json(client: TestClient) -> None:
    response = client.post("/events", content=b"{not json")
    assert response.status_code == 400


def test_partial_batch_success(client: TestClient) -> None:
    events = [_valid_event(), {"bogus": True}, _valid_event(source="syswatch")]
    response = client.post("/events", json=events)
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 2
    assert len(body["rejected"]) == 1