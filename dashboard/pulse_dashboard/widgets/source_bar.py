"""Source breakdown — horizontal bar by source."""

from textual.containers import Container
from textual.widgets import Static

from pulse_dashboard.storage import Storage
from pulse_dashboard.theme import SOURCE_COLOR

class SourceBar(Container):
    DEFAULT_CSS = """
    SourceBar {
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
        counts = self.storage.source_counts(60)
        if not counts:
            self._content.update("[bold #5fafd7]Source (last 60m)[/]\n  [#888888]no events[/]")
            return
        lines = ["[bold #5fafd7]Source (last 60m)[/]"]
        max_n = max(counts.values()) if counts else 1
        for source, n in sorted(counts.items()):
            color = SOURCE_COLOR.get(source, "#e8e8e8")
            bar_width = int((n / max_n) * 20) if max_n else 0
            bar = "█" * bar_width if bar_width else ""
            lines.append(f"  [{color}]{source:<10}[/] {bar:<20} {n}")
        self._content.update("\n".join(lines))
