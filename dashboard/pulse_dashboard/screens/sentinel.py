"""sentinel tab — alert breakdown by detector + recent alerts feed."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, DataTable
from rich.text import Text

from pulse_dashboard.storage import Storage
from pulse_dashboard.theme import SEVERITY_COLOR, TEXT_MUTED


class SentinelScreen(Container):
    DEFAULT_CSS = """
    SentinelScreen {
        layout: vertical;
    }
    SentinelScreen .panel-title {
        color: #5fafd7;
        text-style: bold;
        margin: 1 1 0 1;
    }
    SentinelScreen .top-talkers {
        height: 12;
        margin: 0 1 1 1;
    }
    SentinelScreen .alerts-table {
        height: 1fr;
        margin: 0 1 1 1;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._summary = Static("", classes="panel-title")
        self._top_talkers_title = Static("[bold #5fafd7]Top Talkers (last 24h)[/]", classes="panel-title")
        self._top_talkers = DataTable(zebra_stripes=True, cursor_type="row", classes="top-talkers")
        self._table = DataTable(zebra_stripes=True, cursor_type="row", classes="alerts-table")

    def compose(self) -> ComposeResult:
        yield self._summary
        yield self._top_talkers_title
        yield self._top_talkers
        yield self._table

    def on_mount(self) -> None:
        self._top_talkers.add_columns("Src IP", "Alerts (24h)", "Last Seen")
        self._table.add_columns("Time", "Detector", "Src IP", "Dst IP", "Severity", "Message")
        self.refresh_data()

    def refresh_data(self) -> None:
        counts = self.storage.sentinel_alert_counts_by_detector(60)
        if counts:
            parts = "  ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
            self._summary.update(f"[bold #5fafd7]Detectors (last 60 min)[/]   {parts}")
        else:
            self._summary.update("[bold #5fafd7]Detectors (last 60 min)[/]   [#888888]no alerts in window[/]")

        talkers = self.storage.sentinel_top_talkers(24, 10)
        self._top_talkers.clear()
        if not talkers:
            self._top_talkers.add_row("—", "0", "no alerts in 24h")
        else:
            for talker in talkers:
                src_ip = str(talker["src_ip"])
                src_display = Text(src_ip)
                if self.storage.is_trusted_src_ip(src_ip):
                    src_display.append(" [internal]", style=TEXT_MUTED)
                self._top_talkers.add_row(
                    src_display,
                    str(talker["alert_count"]),
                    str(talker["last_seen"])[11:19],
                )

        # Recent sentinel alerts
        events = [e for e in self.storage.recent_events(limit=50, source="sentinel")
                  if e.event_type == "sentinel.alert"]

        self._table.clear()
        if not events:
            self._table.add_row("—", "—", "—", "—", "—", "no sentinel alerts yet")
            return

        for e in events:
            sev_color = SEVERITY_COLOR.get(e.severity, "#e8e8e8")
            self._table.add_row(
                e.timestamp[11:19],  # HH:MM:SS
                str(e.payload.get("detection_type", "?")),
                str(e.payload.get("src_ip", "?")),
                str(e.payload.get("dst_ip", "?")),
                f"[{sev_color}]{e.severity}[/]",
                str(e.payload.get("message", "")),
            )
