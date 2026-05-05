"""sentinel tab — alert breakdown by detector + recent alerts feed."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widget import Widget
from textual.widgets import Static, DataTable

from codex_dashboard.storage import Storage
from codex_dashboard.theme import SEVERITY_COLOR


class SentinelScreen(Widget):
    """Display sentinel alerts and detectors."""

    DEFAULT_CSS = """
    SentinelScreen {
        layout: vertical;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def compose(self) -> ComposeResult:
        yield Static("[bold #5fafd7]Sentinel Alerts (last 60m)[/bold #5fafd7]")
        counts = self.storage.sentinel_alert_counts_by_detector(60)
        if counts:
            parts = []
            for detector, count in sorted(counts.items()):
                parts.append(f"  {detector}: {count}")
            content = "\n".join(parts) if parts else "[dim]No alerts[/dim]"
        else:
            content = "[dim]No sentinel alerts yet[/dim]"
        yield Static(content)
