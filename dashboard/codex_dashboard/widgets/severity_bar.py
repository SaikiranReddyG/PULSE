"""Severity breakdown — horizontal bar with per-severity counts and colors."""

from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static

from codex_dashboard.storage import Storage
from codex_dashboard.theme import SEVERITY_COLOR


class SeverityBar(Widget):
    """Display event count breakdown by severity."""

    DEFAULT_CSS = """
    SeverityBar {
        height: 3;
        border: round $border;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def render(self) -> str:
        """Render severity breakdown with color coding."""
        if not self.storage.is_available():
            return "[dim]No data[/dim]"

        counts = self.storage.severity_counts(60)

        # Build severity line with colors
        parts = ["[bold #5fafd7]Severity (last 60m)[/bold #5fafd7]\n"]
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = counts.get(sev, 0)
            color = SEVERITY_COLOR.get(sev, "#888888")
            parts.append(f"[{color}]{sev.title():8}[/{color}]: {count} ")

        return "".join(parts)
