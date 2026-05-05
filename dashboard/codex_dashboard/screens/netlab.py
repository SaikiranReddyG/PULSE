"""netlab tab — recent scenario runs and current activity."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable

from codex_dashboard.storage import Storage


class NetlabScreen(Widget):
    """Display netlab scenario runs."""

    DEFAULT_CSS = """
    NetlabScreen {
        layout: vertical;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def compose(self) -> ComposeResult:
        yield Static("[bold #5fafd7]Netlab Scenarios[/bold #5fafd7]")
        scenarios = self.storage.netlab_recent_scenarios(limit=10)
        if scenarios:
            parts = []
            for s in scenarios:
                parts.append(f"  {s['timestamp']}: {s['scenario']}")
            content = "\n".join(parts[:5])  # Show first 5
        else:
            content = "[dim]No netlab scenarios yet[/dim]"
        yield Static(content)
