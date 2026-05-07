"""syswatch tab — latest CPU/memory/disk/network metrics."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static

from codex_dashboard.storage import Storage


class SyswatchScreen(Container):
    DEFAULT_CSS = """
    SyswatchScreen {
        layout: vertical;
    }
    SyswatchScreen .metric-panel {
        border: round #333333;
        padding: 1 2;
        margin: 1;
        height: auto;
    }
    SyswatchScreen .metric-title {
        color: #5fafd7;
        text-style: bold;
    }
    SyswatchScreen .no-data {
        color: #888888;
    }
    """

    def __init__(self, storage: Storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self._cpu = Static("", classes="metric-panel")
        self._memory = Static("", classes="metric-panel")
        self._disk = Static("", classes="metric-panel")
        self._network = Static("", classes="metric-panel")
        self._anomalies = Static("", classes="metric-panel")

    def compose(self) -> ComposeResult:
        yield self._cpu
        yield self._memory
        yield self._disk
        yield self._network
        yield self._anomalies

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        m = self.storage.syswatch_latest_metrics()

        if m["cpu"]:
            p = m["cpu"].payload
            self._cpu.update(
                f"[bold #5fafd7]CPU[/]  [dim]({m['cpu'].timestamp})[/]\n"
                f"  Usage: {p.get('usage_pct', '?')}%   "
                f"User: {p.get('user_pct', '?')}%   "
                f"System: {p.get('system_pct', '?')}%   "
                f"Idle: {p.get('idle_pct', '?')}%   "
                f"Cores: {p.get('core_count', '?')}"
            )
        else:
            self._cpu.update("[bold #5fafd7]CPU[/]\n  [#888888]no syswatch.metrics.cpu events yet[/]")

        if m["memory"]:
            p = m["memory"].payload
            total = int(p.get("mem_total", 0))
            used = int(p.get("mem_used", 0))
            pct = (used / total * 100.0) if total else 0
            self._memory.update(
                f"[bold #5fafd7]Memory[/]  [dim]({m['memory'].timestamp})[/]\n"
                f"  Used: {used:,} / {total:,} kB ({pct:.1f}%)   "
                f"Available: {int(p.get('mem_available', 0)):,} kB   "
                f"Swap used: {int(p.get('swap_used', 0)):,} / {int(p.get('swap_total', 0)):,} kB"
            )
        else:
            self._memory.update("[bold #5fafd7]Memory[/]\n  [#888888]no syswatch.metrics.memory events yet[/]")

        if m["disk"]:
            p = m["disk"].payload
            disks = p.get("disks", [])
            lines = [f"[bold #5fafd7]Disk[/]  [dim]({m['disk'].timestamp})[/]"]
            if disks:
                for d in disks[:6]:
                    lines.append(f"  {d.get('device', '?'):<20} read: {d.get('read_bps', '?')}   write: {d.get('write_bps', '?')}")
            else:
                lines.append("  [#888888](no disks reported)[/]")
            self._disk.update("\n".join(lines))
        else:
            self._disk.update("[bold #5fafd7]Disk[/]\n  [#888888]no syswatch.metrics.disk events yet[/]")

        if m["network"]:
            p = m["network"].payload
            ifaces = p.get("interfaces", [])
            lines = [f"[bold #5fafd7]Network[/]  [dim]({m['network'].timestamp})[/]"]
            if ifaces:
                for i in ifaces[:6]:
                    lines.append(f"  {i.get('name', '?'):<20} rx: {i.get('rx_bps', '?')}   tx: {i.get('tx_bps', '?')}")
            else:
                lines.append("  [#888888](no interfaces reported)[/]")
            self._network.update("\n".join(lines))
        else:
            self._network.update("[bold #5fafd7]Network[/]\n  [#888888]no syswatch.metrics.network events yet[/]")

        recent_signals = self.storage.syswatch_recent_signals()
        signal_lines = ["[bold #5fafd7]Recent Anomalies & Lifecycle[/]"]
        if recent_signals:
            for e in recent_signals:
                summary = " ".join(f"{k}={v}" for k, v in list(e.payload.items())[:3] if not isinstance(v, (list, dict)))
                signal_lines.append(f"  [dim]{e.timestamp[11:19]}[/] {e.severity} {e.event_type} {summary}")
        else:
            signal_lines.append("  [#888888]no syswatch.anomaly or syswatch.lifecycle events yet[/]")
        self._anomalies.update("\n".join(signal_lines))
