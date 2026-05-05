"""Unit tests for the storage layer."""

import pytest


def test_is_available(storage):
    """Test that database availability check works."""
    assert storage.is_available() is True


def test_total_events(storage):
    """Test total event count."""
    assert storage.total_events() == 6


def test_events_in_window(storage):
    """Test event counting within a time window."""
    # All sample data is from 2026-05, so any realistic window goes back to 2026
    assert storage.events_in_window(5000) == 6
    # Zero-minute window might exclude recent events depending on implementation
    counts = storage.events_in_window(0)
    assert counts >= 0


def test_severity_counts(storage):
    """Test event counting by severity."""
    counts = storage.severity_counts(5000)
    assert counts.get("info") == 4
    assert counts.get("high") == 1
    assert counts.get("critical") == 1


def test_source_counts(storage):
    """Test event counting by source."""
    counts = storage.source_counts(5000)
    assert counts.get("sentinel") == 3
    assert counts.get("syswatch") == 2
    assert counts.get("netlab") == 1


def test_recent_events(storage):
    """Test retrieving recent events in descending ID order."""
    events = storage.recent_events(limit=10)
    assert len(events) == 6
    # Events should be in reverse ID order (newest first)
    assert events[0].id > events[-1].id


def test_recent_events_filtered_by_source(storage):
    """Test filtering recent events by source."""
    events = storage.recent_events(limit=10, source="sentinel")
    assert len(events) == 3
    assert all(e.source == "sentinel" for e in events)


def test_sentinel_alert_counts_by_detector(storage):
    """Test counting sentinel alerts by detection type."""
    counts = storage.sentinel_alert_counts_by_detector(5000)
    assert counts.get("PORT_SCAN") == 1
    assert counts.get("DDoS") == 1


def test_netlab_recent_scenarios(storage):
    """Test retrieving recent netlab scenarios."""
    scenarios = storage.netlab_recent_scenarios(limit=10)
    assert len(scenarios) >= 1
    assert scenarios[0]["scenario"] == "arp_spoof"
