"""Main Textual app for pulse-dashboard."""

from __future__ import annotations
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, TabbedContent, TabPane, Static

from pulse_dashboard.storage import Storage
from pulse_dashboard.screens.overview import OverviewScreen
from pulse_dashboard.screens.syswatch import SyswatchScreen
from pulse_dashboard.screens.sentinel import SentinelScreen
from pulse_dashboard.screens.netlab import NetlabScreen


REFRESH_INTERVAL_SECONDS = 5.0


class PulseDashboardApp(App):
    """Terminal dashboard for pulse-platform."""

    CSS_PATH = str(Path(__file__).parent / "styles.tcss")
    TITLE = "pulse"
    SUB_TITLE = "platform dashboard"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh", priority=True),
        Binding("1", "switch_tab('overview')", "Overview"),
        Binding("2", "switch_tab('syswatch')", "syswatch"),
        Binding("3", "switch_tab('sentinel')", "sentinel"),
        Binding("4", "switch_tab('netlab')", "netlab"),
    ]

    def __init__(self, db_path: str):
        super().__init__()
        self.storage = Storage(db_path)
        self._db_path = db_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="overview"):
            with TabPane("Overview", id="overview"):
                yield OverviewScreen(self.storage, id="overview-screen")
            with TabPane("syswatch", id="syswatch"):
                yield SyswatchScreen(self.storage, id="syswatch-screen")
            with TabPane("sentinel", id="sentinel"):
                yield SentinelScreen(self.storage, id="sentinel-screen")
            with TabPane("netlab", id="netlab"):
                yield NetlabScreen(self.storage, id="netlab-screen")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_status_bar()
        self.set_interval(REFRESH_INTERVAL_SECONDS, self._tick)

    def _tick(self) -> None:
        self._refresh_all_screens()
        self._refresh_status_bar()

    def _refresh_all_screens(self) -> None:
        for screen in self.query("OverviewScreen, SyswatchScreen, SentinelScreen, NetlabScreen"):
            if hasattr(screen, "refresh_data"):
                screen.refresh_data()

    def _refresh_status_bar(self) -> None:
        bar = self.query_one("#status-bar", Static)
        if not self.storage.is_available():
            bar.update(f"[red]✗ database unavailable: {self._db_path}[/]")
            return
        total = self.storage.total_events()
        recent = self.storage.events_in_window(5)
        bar.update(
            f"[green]●[/] db OK  "
            f"[white]events:[/] {total}  "
            f"[white]last 5min:[/] {recent}  "
            f"[dim]q: quit  r: refresh  1-4: tabs[/]"
        )

    def action_refresh(self) -> None:
        self._tick()

    def action_switch_tab(self, tab_id: str) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = tab_id
