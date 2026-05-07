"""Recent events table for the Overview tab — last 50 events, color-coded by severity."""

from textual.containers import Container
from textual.widgets import DataTable

from codex_dashboard.storage import Storage
from codex_dashboard.theme import SEVERITY_COLOR

class RecentEventsTable(Container):
    DEFAULT_CSS = """
    RecentEventsTable {
        border: round #333333;
        padding: 0 1;
    }
    RecentEventsTable DataTable {
        height: 1fr;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._table = DataTable(zebra_stripes=True, cursor_type="row")

    def compose(self):
        yield self._table

    def on_mount(self) -> None:
        self._table.add_columns("Time", "Source", "Event Type", "Severity", "Summary")
        self.refresh_data()

    def refresh_data(self) -> None:
        events = self.storage.recent_events(limit=50, exclude_routine=True)
        self._table.clear()
        if not events:
            self._table.add_row("—", "—", "—", "—", "no events yet")
            return
        for e in events:
            sev_color = SEVERITY_COLOR.get(e.severity, "#e8e8e8")
            summary = self._summarize_payload(e.payload)
            self._table.add_row(
                e.timestamp[11:19],  # HH:MM:SS
                e.source,
                e.event_type,
                f"[{sev_color}]{e.severity}[/]",
                summary,
            )

    @staticmethod
    def _summarize_payload(payload: dict) -> str:
        # Pick first 2-3 informative keys, ignore long lists/dicts
        if not isinstance(payload, dict) or not payload:
            return "—"
        parts = []
        for k, v in list(payload.items())[:3]:
            if isinstance(v, (list, dict)):
                continue
            parts.append(f"{k}={v}")
        return " ".join(parts) if parts else "—"
