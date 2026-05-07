"""Severity breakdown — horizontal bar with per-severity counts and colors."""

from textual.containers import Container
from textual.widgets import Static

from codex_dashboard.storage import Storage
from codex_dashboard.theme import SEVERITY_COLOR

class SeverityBar(Container):
    DEFAULT_CSS = """
    SeverityBar {
        border: round #333333;
        padding: 1 2;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._content = Static("")

    def compose(self):
        yield self._content

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        counts = self.storage.severity_counts(60)
        if not counts:
            self._content.update("[bold #5fafd7]Severity (last 60m)[/]\n  [#888888]no events[/]")
            return
        order = ["info", "low", "medium", "high", "critical"]
        lines = ["[bold #5fafd7]Severity (last 60m)[/]"]
        max_n = max(counts.values()) if counts else 1
        for sev in order:
            n = counts.get(sev, 0)
            color = SEVERITY_COLOR.get(sev, "#e8e8e8")
            bar_width = int((n / max_n) * 20) if max_n else 0
            bar = "█" * bar_width if bar_width else ""
            lines.append(f"  [{color}]{sev:<9}[/] {bar:<20} {n}")
        self._content.update("\n".join(lines))
