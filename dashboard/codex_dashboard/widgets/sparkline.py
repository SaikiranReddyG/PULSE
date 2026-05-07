"""Events-per-minute sparkline using Textual's built-in Sparkline."""

from textual.containers import Container
from textual.widgets import Static, Sparkline

from codex_dashboard.storage import Storage

class EventsSparkline(Container):
    DEFAULT_CSS = """
    EventsSparkline {
        border: round #333333;
        padding: 1 2;
    }
    EventsSparkline .panel-title {
        color: #5fafd7;
        text-style: bold;
    }
    EventsSparkline Sparkline {
        height: 5;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._title = Static("[bold #5fafd7]Non-routine events / min (last 60)[/]")
        self._sparkline = Sparkline([0] * 60, summary_function=max)

    def compose(self):
        yield self._title
        yield self._sparkline

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        series = self.storage.events_per_minute(60)
        # Pad to 60 minutes, even if some are missing
        values = [count for (_, count) in series]
        if len(values) < 60:
            values = [0] * (60 - len(values)) + values
        self._sparkline.data = values
