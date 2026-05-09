# pulse-dashboard

Terminal dashboard for pulse-platform. Built with Textual.

## Install

```bash
cd dashboard
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Run

```bash
.venv/bin/pulse-dashboard
```

Set `PULSE_DB` env var to override database path.

## Keys

- `q` quit
- `r` refresh
- `1-4` switch tabs

## Tabs

- Overview: total events, severity/source breakdown, recent events
- Syswatch: latest CPU and memory metrics
- Sentinel: alert counts by detector (last 60m)
- Netlab: recent scenario runs
