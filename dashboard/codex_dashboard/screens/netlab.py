"""netlab tab — recent scenario runs and current activity."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable

from codex_dashboard.storage import Storage


class NetlabScreen(Widget):
    DEFAULT_CSS = """
    NetlabScreen {
        layout: vertical;
    }
    NetlabScreen .panel-title {
        color: #5fafd7;
        text-style: bold;
        margin: 1 1 0 1;
    }
    NetlabScreen DataTable {
        height: 1fr;
        margin: 0 1 1 1;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._title = Static("[bold #5fafd7]Recent scenarios[/]", classes="panel-title")
        self._table = DataTable(zebra_stripes=True, cursor_type="row")

    def compose(self) -> ComposeResult:
        yield self._title
        yield self._table

    def on_mount(self) -> None:
        self._table.add_columns("Started", "Scenario", "Status")
        self.refresh_data()

    def refresh_data(self) -> None:
        scenarios = self.storage.netlab_recent_scenarios(limit=15)
        self._table.clear()
        if not scenarios:
            self._table.add_row("—", "—", "no netlab runs yet")
            return
        for s in scenarios:
            self._table.add_row(
                s["started_at"][11:19],
                s["scenario"],
                s["status"],
            )
