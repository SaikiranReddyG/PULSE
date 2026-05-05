"""Events-per-minute sparkline."""

from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static

from codex_dashboard.storage import Storage


class EventsSparkline(Widget):
    """Display a simple ASCII sparkline of events over time."""

    DEFAULT_CSS = """
    EventsSparkline {
        height: 3;
        border: round $border;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def render(self) -> str:
        """Render a time-series visualization of events."""
        if not self.storage.is_available():
            return "[dim]No data[/dim]"

        # For now, just show the last 60 minutes count
        # A full sparkline would require more detailed time-series data
        count_60 = self.storage.events_in_window(60)
        count_30 = self.storage.events_in_window(30)
        count_10 = self.storage.events_in_window(10)

        return (
            f"[bold #5fafd7]Events (time series)[/bold #5fafd7]\n"
            f"60m: {count_60} events  30m: {count_30}  10m: {count_10}"
        )
