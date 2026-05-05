"""Main Textual app for codex-dashboard."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static


class CodexDashboardApp(App):
    """Terminal dashboard for codex-platform."""

    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    TITLE = "codex"

    def __init__(self, db_path: str = ""):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"codex-dashboard — SQLite: {self.db_path}")
        yield Footer()

    def action_refresh(self) -> None:
        """Force a refresh of all data."""
        pass


if __name__ == "__main__":
    app = CodexDashboardApp()
    app.run()
