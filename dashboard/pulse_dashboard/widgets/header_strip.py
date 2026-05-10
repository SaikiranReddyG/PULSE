"""Header strip — total events, events/min, source counts, and source liveness."""

from datetime import datetime, timezone, timedelta

from textual.containers import Container
from textual.widgets import Static

from pulse_dashboard.storage import Storage
from pulse_dashboard.theme import ACCENT, SOURCE_COLOR, TEXT_MUTED


LIVENESS_THRESHOLDS_MINUTES = {
    "sentinel": 10,
    "syswatch": 5,
    "netlab": 10,
}

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
            self._content.update(f"[#d75f5f]database unavailable[/]\n[dim]waiting for receiver[/]")
            return
        total = self.storage.total_events()
        last_min = self.storage.events_in_window(1)
        last_hour = self.storage.events_in_window(60)
        sources = self.storage.source_counts(60)
        last_seen = self.storage.last_seen_by_source()
        src_str = "   ".join(f"[{SOURCE_COLOR.get(k, TEXT_MUTED)}]{k}[/] [#888888]{v}[/]" for k, v in sorted(sources.items()))
        liveness_str = "   ".join(self._format_liveness(source, last_seen.get(source)) for source in ("sentinel", "syswatch", "netlab"))
        self._content.update(
            f"[bold {ACCENT}]Total[/] {total}    "
            f"[bold {ACCENT}]Last 1m[/] {last_min}    "
            f"[bold {ACCENT}]Last 1h[/] {last_hour}\n"
            f"{src_str}\n"
            f"{liveness_str}"
        )

    def _format_liveness(self, source: str, timestamp: str | None) -> str:
        source_color = SOURCE_COLOR.get(source, TEXT_MUTED)
        threshold_minutes = LIVENESS_THRESHOLDS_MINUTES[source]
        if timestamp is None:
            return f"[{source_color}]{source}[/] [#d75f5f]●[/] STALE"

        try:
            seen_at = datetime.fromisoformat(timestamp)
        except ValueError:
            return f"[{source_color}]{source}[/] [#d75f5f]●[/] STALE"

        if seen_at.tzinfo is None:
            seen_at = seen_at.replace(tzinfo=timezone.utc)
        seen_at_utc = seen_at.astimezone(timezone.utc)
        age = datetime.now(timezone.utc) - seen_at_utc
        seen_time = seen_at_utc.strftime("%H:%M:%S")
        threshold = timedelta(minutes=threshold_minutes)
        if age <= threshold:
            return f"[{source_color}]{source}[/] [#87af5f]●[/] {seen_time}"
        if age <= threshold * 2:
            return f"[{source_color}]{source}[/] [#d7af5f]●[/] {seen_time}"
        return f"[{source_color}]{source}[/] [#d75f5f]●[/] STALE"
