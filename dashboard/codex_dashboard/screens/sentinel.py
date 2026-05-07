"""sentinel tab — alert breakdown by detector + recent alerts feed."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, DataTable

from codex_dashboard.storage import Storage
from codex_dashboard.theme import SEVERITY_COLOR


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
    SentinelScreen DataTable {
        height: 1fr;
        margin: 0 1 1 1;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._summary = Static("", classes="panel-title")
        self._table = DataTable(zebra_stripes=True, cursor_type="row")

    def compose(self) -> ComposeResult:
        yield self._summary
        yield self._table

    def on_mount(self) -> None:
        self._table.add_columns("Time", "Detector", "Src IP", "Dst IP", "Severity", "Message")
        self.refresh_data()

    def refresh_data(self) -> None:
        counts = self.storage.sentinel_alert_counts_by_detector(60)
        if counts:
            parts = "  ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
            self._summary.update(f"[bold #5fafd7]Detectors (last 60 min)[/]   {parts}")
        else:
            self._summary.update("[bold #5fafd7]Detectors (last 60 min)[/]   [#888888]no alerts in window[/]")

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
