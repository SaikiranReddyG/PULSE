"""Main Textual app for codex-dashboard."""

from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane

from codex_dashboard.storage import Storage
from codex_dashboard.screens.overview import OverviewScreen


REFRESH_INTERVAL_SECONDS = 5.0


class CodexDashboardApp(App):
    """Terminal dashboard for codex-platform."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("1", "tab(0)", "Overview", show=False),
        Binding("2", "tab(1)", "Syswatch", show=False),
        Binding("3", "tab(2)", "Sentinel", show=False),
        Binding("4", "tab(3)", "Netlab", show=False),
    ]

    TITLE = "codex"

    def __init__(self, db_path: str = "", **kwargs):
        super().__init__(**kwargs)
        self.db_path = db_path
        self.storage = Storage(db_path)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Overview"):
                yield OverviewScreen(self.storage)
            with TabPane("Syswatch"):
                yield Static("[dim](coming next phase)[/dim]")
            with TabPane("Sentinel"):
                yield Static("[dim](coming next phase)[/dim]")
            with TabPane("Netlab"):
                yield Static("[dim](coming next phase)[/dim]")
        yield Footer()

    def on_mount(self) -> None:
        """Start periodic refresh task."""
        self.set_interval(REFRESH_INTERVAL_SECONDS, self.action_refresh)

    def action_tab(self, index: int) -> None:
        """Switch to a tab by index (0-3)."""
        self.query_one(TabbedContent).active = index

    def action_refresh(self) -> None:
        """Force a refresh of all data."""
        # Trigger re-render of Overview widgets
        overview = self.query_one(OverviewScreen, expect_type=OverviewScreen)
        if overview:
            overview.refresh_data()


if __name__ == "__main__":
    app = CodexDashboardApp()
    app.run()
