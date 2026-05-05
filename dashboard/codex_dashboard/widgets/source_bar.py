"""Source breakdown — horizontal bar by source."""

from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static

from codex_dashboard.storage import Storage
from codex_dashboard.theme import SOURCE_COLOR


class SourceBar(Widget):
    """Display event count breakdown by source."""

    DEFAULT_CSS = """
    SourceBar {
        height: 3;
        border: round $border;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def render(self) -> str:
        """Render source breakdown with colors."""
        if not self.storage.is_available():
            return "[dim]No data[/dim]"

        counts = self.storage.source_counts(60)

        # Build source line with colors
        parts = ["[bold #5fafd7]Source (last 60m)[/bold #5fafd7]\n"]
        for src in ["syswatch", "sentinel", "netlab"]:
            count = counts.get(src, 0)
            color = SOURCE_COLOR.get(src, "#888888")
            parts.append(f"[{color}]{src.title():10}[/{color}]: {count} ")

        return "".join(parts)
