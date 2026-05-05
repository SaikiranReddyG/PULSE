"""Header strip — total events, events/min, source counts."""

from textual.widget import Widget
from textual.widgets import Static

from codex_dashboard.storage import Storage


from textual.containers import Container

class HeaderStrip(Container):
    DEFAULT_CSS = """
    HeaderStrip {
        height: 3;
        padding: 0 1;
    }
    HeaderStrip Static {
        height: 3;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._content = Static("", id="header-strip-content")

    def compose(self):
        yield self._content

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        if not self.storage.is_available():
            self._content.update("[#d75f5f]database unavailable[/]")
            return
        total = self.storage.total_events()
        last_min = self.storage.events_in_window(1)
        last_hour = self.storage.events_in_window(60)
        sources = self.storage.source_counts(60)
        src_str = "   ".join(f"[#888888]{k}:[/] {v}" for k, v in sorted(sources.items()))
        self._content.update(
            f"[bold #5fafd7]Total[/] {total}    "
            f"[bold #5fafd7]Last 1m[/] {last_min}    "
            f"[bold #5fafd7]Last 1h[/] {last_hour}\n"
            f"{src_str}"
        )
