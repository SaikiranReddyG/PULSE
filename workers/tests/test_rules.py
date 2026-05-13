from datetime import datetime, timedelta

from workers.rules import AlertRules


def test_critical_passes() -> None:
    rules = AlertRules()

    assert rules.should_throttle("critical", datetime.utcnow()) is False


def test_warning_throttled() -> None:
    rules = AlertRules()

    assert rules.should_throttle("warning", datetime.utcnow() - timedelta(minutes=1)) is True


def test_warning_unthrottled() -> None:
    rules = AlertRules()

    assert rules.should_throttle("warning", datetime.utcnow() - timedelta(minutes=61)) is False


def test_info_suppressed() -> None:
    rules = AlertRules()

    assert rules.should_throttle("info", None) is True


def test_unknown_severity_returns_none() -> None:
    rules = AlertRules()

    assert rules.tier_for_sentinel_alert("unexpected") is None