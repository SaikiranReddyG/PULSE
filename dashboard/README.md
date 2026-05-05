# codex-dashboard

A terminal-native dashboard for codex-platform v0.2+. Built with Textual. Reads SQLite directly in read-only mode.

## What it is

`codex-dashboard` is a CLI tool that runs a responsive terminal UI (TUI) in your terminal. It displays real-time event data from the codex-platform's SQLite database across four tabs: Overview, syswatch, sentinel, and netlab.

## Install

1. In a Python 3.10+ virtual environment:

```bash
cd dashboard
python3 -m venv .venv
.venv/bin/pip install -e .
```

2. From anywhere, run:

```bash
codex-dashboard
```

The dashboard will auto-discover the SQLite database at `~/codex-workspace/codex-platform/sqlite/codex.db` or wherever the stack is running.

To point to a custom database, set `CODEX_DB`:

```bash
CODEX_DB=/path/to/codex.db codex-dashboard
```

## Keys

- `q` — Quit
- `r` — Force refresh
- `1`, `2`, `3`, `4` — Switch to Overview, syswatch, sentinel, or netlab tab

## Tabs

- **Overview** — Event counts, severity breakdown, recent events log.
- **syswatch** — Latest CPU, memory, disk, and network metrics.
- **sentinel** — Alert breakdown by detection type + recent alerts feed.
- **netlab** — Recent scenario runs and activity.

## Theme

Colors are minimal and purposeful. Severity levels (info, low, medium, high, critical) are color-coded. The UI is dark and clean — suitable for extended viewing.
