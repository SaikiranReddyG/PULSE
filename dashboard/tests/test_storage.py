"""Unit tests for the storage layer."""

import sqlite3

import pytest


def test_is_available(storage):
    assert storage.is_available() is True


def test_total_events(storage):
    assert storage.total_events() == 6


def test_events_in_window(storage):
    # Just-inserted rows fall within any positive window
    assert storage.events_in_window(60) == 6


def test_severity_counts(storage):
    counts = storage.severity_counts(60)
    assert counts.get("info") == 5
    assert counts.get("high") == 1


def test_source_counts(storage):
    counts = storage.source_counts(60)
    assert counts.get("sentinel") == 2
    assert counts.get("netlab") == 2
    assert counts.get("syswatch") == 2


def test_recent_events(storage):
    events = storage.recent_events(limit=10)
    assert len(events) == 6
    # Most-recent first
    assert events[0].id > events[-1].id


def test_recent_events_filtered_by_source(storage):
    events = storage.recent_events(limit=10, source="sentinel")
    assert len(events) == 2
    assert all(e.source == "sentinel" for e in events)


def test_syswatch_latest_metrics(storage):
    m = storage.syswatch_latest_metrics()
    assert m["cpu"] is not None
    assert m["cpu"].payload["usage_pct"] == 7.7
    assert m["memory"] is not None
    # No disk / network in fixture
    assert m["disk"] is None
    assert m["network"] is None


def test_sentinel_alert_counts_by_detector(storage):
    counts = storage.sentinel_alert_counts_by_detector(60)
    assert counts.get("PORT_SCAN") == 1


def test_sentinel_top_talkers(storage):
    talkers = storage.sentinel_top_talkers(24, 10)
    assert len(talkers) == 1
    assert talkers[0]["src_ip"] == "1.2.3.4"
    assert talkers[0]["alert_count"] == 1


def test_netlab_recent_scenarios(storage):
    scenarios = storage.netlab_recent_scenarios(limit=10)
    assert len(scenarios) >= 1
    assert scenarios[0]["scenario"] == "arp_spoof"


def test_last_seen_by_source(storage):
    with sqlite3.connect(storage.db_path) as conn:
        known_timestamp = conn.execute(
            "SELECT timestamp FROM events WHERE source = ? LIMIT 1",
            ("sentinel",),
        ).fetchone()[0]

        conn.execute("DELETE FROM events WHERE source = ?", ("netlab",))
        conn.commit()

    last_seen = storage.last_seen_by_source()
    assert last_seen["sentinel"] == known_timestamp
    assert last_seen["syswatch"] == known_timestamp
    assert last_seen["netlab"] is None
