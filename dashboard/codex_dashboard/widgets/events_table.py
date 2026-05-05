"""Recent events table for the Overview tab — last 50 events, color-coded by severity."""

from __future__ import annotations

from textual.widget import Widget
from textual.widgets import DataTable, Static

from codex_dashboard.storage import Storage
from codex_dashboard.theme import SEVERITY_COLOR


class RecentEventsTable(Widget):
    """Display a table of recent events, color-coded by severity."""

    DEFAULT_CSS = """
    RecentEventsTable {
        height: 1fr;
        border: round $border;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.table = DataTable()

    def compose(self):
        """Create the data table widget."""
        yield self.table

    def on_mount(self):
        """Initialize table columns and load data."""
        self.table.add_columns(
            "ID", "Timestamp", "Source", "Type", "Severity", "Payload"
        )
        self.refresh_data()

    def refresh_data(self):
        """Load recent events from storage."""
        self.table.clear()
        if not self.storage.is_available():
            return

        events = self.storage.recent_events(limit=50)
        for event in events:
            ts = event.timestamp.strftime("%H:%M:%S")
            payload_key = next(iter(event.payload.keys())) if event.payload else "—"
            payload_val = event.payload.get(payload_key, "—")
            if isinstance(payload_val, (dict, list)):
                payload_str = "…"
            else:
                payload_str = str(payload_val)[:20]

            color = SEVERITY_COLOR.get(event.severity, "#888888")
            sev_colored = f"[{color}]{event.severity}[/{color}]"

            self.table.add_row(
                str(event.id),
                ts,
                event.source,
                event.event_type,
                sev_colored,
                payload_str,
            )
