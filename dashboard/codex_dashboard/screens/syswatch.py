"""syswatch tab — latest CPU/memory/disk/network metrics."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widget import Widget
from textual.widgets import Static

from codex_dashboard.storage import Storage


class SyswatchScreen(Widget):
    """Display latest syswatch metrics."""

    DEFAULT_CSS = """
    SyswatchScreen {
        layout: vertical;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def compose(self) -> ComposeResult:
        yield Static("[bold #5fafd7]syswatch Metrics[/bold #5fafd7]")
        metrics = self.storage.syswatch_latest_metrics()
        if metrics:
            content = "CPU: {:.1f}% | Memory: {:.1f}%".format(
                metrics.get("cpu_percent", 0), metrics.get("mem_percent", 0)
            )
        else:
            content = "[dim]No syswatch.metrics events yet[/dim]"
        yield Static(content)
