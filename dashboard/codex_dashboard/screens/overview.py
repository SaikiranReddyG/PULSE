"""Overview tab — header strip + sparkline + severity/source bars + recent events."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget

from codex_dashboard.storage import Storage
from codex_dashboard.widgets.header_strip import HeaderStrip
from codex_dashboard.widgets.sparkline import EventsSparkline
from codex_dashboard.widgets.severity_bar import SeverityBar
from codex_dashboard.widgets.source_bar import SourceBar
from codex_dashboard.widgets.events_table import RecentEventsTable


class OverviewScreen(Widget):
    """Overview tab: header + sparkline + breakdown bars + events table."""

    DEFAULT_CSS = """
    OverviewScreen {
        layout: vertical;
        background: $background;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def compose(self) -> ComposeResult:
        yield HeaderStrip(self.storage)
        yield EventsSparkline(self.storage)
        yield SeverityBar(self.storage)
        yield SourceBar(self.storage)
        yield RecentEventsTable(self.storage)

    def refresh_data(self):
        """Refresh all child widgets."""
        for child in self.query("*"):
            if hasattr(child, "refresh_data"):
                child.refresh_data()
            else:
                child.update("")  # Trigger re-render
