"""Header strip — total events, events/min, source counts."""

from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static

from codex_dashboard.storage import Storage


class HeaderStrip(Widget):
    """Display summary metrics at the top of Overview tab."""

    DEFAULT_CSS = """
    HeaderStrip {
        height: 3;
        border: round $border;
        background: $surface;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def render(self) -> str:
        """Render the header strip with live data."""
        if not self.storage.is_available():
            return "[dim]Database unavailable[/dim]"

        total = self.storage.total_events()
        recent = self.storage.events_in_window(60)

        sources = self.storage.source_counts(60)
        source_str = " • ".join(
            f"{src.title()}: {sources.get(src, 0)}"
            for src in ["sentinel", "syswatch", "netlab"]
        )

        return (
            f"[bold #5fafd7]Events[/bold #5fafd7] Total: {total}  "
            f"Last 60m: {recent}\n"
            f"[dim]{source_str}[/dim]"
        )
