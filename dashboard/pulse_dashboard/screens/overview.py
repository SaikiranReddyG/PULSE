"""Overview tab — header strip + sparkline + severity/source bars + recent events."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widget import Widget
from textual.widgets import Static

from pulse_dashboard.storage import Storage
from pulse_dashboard.widgets.header_strip import HeaderStrip
from pulse_dashboard.widgets.sparkline import EventsSparkline
from pulse_dashboard.widgets.severity_bar import SeverityBar
from pulse_dashboard.widgets.source_bar import SourceBar
from pulse_dashboard.widgets.events_table import RecentEventsTable


class OverviewScreen(Container):
    DEFAULT_CSS = """
    OverviewScreen {
        layout: vertical;
    }
    OverviewScreen #top-row {
        height: auto;
    }
    OverviewScreen #middle-row {
        height: 12;
    }
    OverviewScreen #bottom-row {
        height: 1fr;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def compose(self) -> ComposeResult:
        with Container(id="top-row"):
            yield HeaderStrip(self.storage, id="header-strip")
        with Horizontal(id="middle-row"):
            yield EventsSparkline(self.storage, id="sparkline")
            yield SeverityBar(self.storage, id="severity-bar")
            yield SourceBar(self.storage, id="source-bar")
        with Container(id="bottom-row"):
            yield RecentEventsTable(self.storage, id="events-table")

    def refresh_data(self) -> None:
        for child_id in ["header-strip", "sparkline", "severity-bar", "source-bar", "events-table"]:
            try:
                w = self.query_one(f"#{child_id}")
            except Exception:
                continue
            if hasattr(w, "refresh_data"):
                w.refresh_data()
