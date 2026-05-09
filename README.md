# pulse-platform

`pulse-platform` is a single-host SOC integration stack. It receives pulse-contract JSON events from three sibling tools, `sentinel` (network IDS), `netlab` (attack/defense lab), and `syswatch` (system monitor), then persists, alerts on, and visualizes those events.

It is not a multi-host SIEM, not a managed service, and not a fleet manager. It runs on one Linux box. The security tools themselves live in separate repos and emit events to this platform's HTTP receiver.

## Services

The stack is three containers (plus optional n8n):

| Service | Purpose |
|---|---|
| `receiver` | HTTP API that accepts contract events, validates them, writes SQLite, and fans out to Redis Streams and Discord alerts |
| `redis` | Live event tail via Redis Streams |
| `n8n` | Optional profile for future workflow automation |

The dashboard runs locally as a terminal application and reads SQLite directly in read-only mode.

## Quick Start

```bash
git clone <repo-url> pulse-platform && cd pulse-platform
cp .env.example .env
# edit .env to set passwords and (optionally) DISCORD_WEBHOOK_URL
make up

# Verify the receiver is up
curl http://127.0.0.1:8765/health
# → {"status":"ok"}

# In another terminal, launch the dashboard
cd dashboard
python3 -m venv .venv
.venv/bin/pip install -e .
pulse-dashboard
# or simply: make dashboard (from the root directory)

# Stop
make down
```

## How Tools Connect

Each pulse tool supports an `http_post` output destination. Point it at the receiver endpoint:

```bash
sudo sentinel run -i wlo1 --output http_post --output-url http://127.0.0.1:8765/events
sudo netlab run arp_spoof --output http_post --output-url http://127.0.0.1:8765/events
syswatch --config syswatch.yaml  # configure http_post in syswatch.yaml
```

## Architecture

```text
┌───────────┐   ┌───────────┐   ┌───────────┐
│ sentinel  │   │  netlab   │   │ syswatch  │
└─────┬─────┘   └─────┬─────┘   └─────┬─────┘
      │ HTTP POST     │ HTTP POST     │ HTTP POST
      └───────────────┼───────────────┘
                      ▼
               ┌──────────────┐
               │   receiver   │  validates, persists, fans out
               └──┬────────┬──┘
                  │        │
           ┌──────▼──┐  ┌──▼──────┐
           │ SQLite  │  │ Redis   │
           │ (cold)  │  │ (hot)   │
           └────┬────┘  └─────────┘
                ▼
        pulse-dashboard
        (Textual TUI terminal app)
        reads SQLite directly

Optional: Discord webhook on high/critical events
```

## Configuration

Copy `.env.example` to `.env` and edit the passwords and any optional alerting settings. The receiver and Redis ports are localhost-only by default.

## Dashboard

The dashboard is a terminal-native tool built with Textual. It reads the SQLite database directly in read-only mode (no writes possible—safe to run concurrently).

See [dashboard/README.md](dashboard/README.md) for installation and usage details.

```bash
make dashboard
```

Press `q` to quit, `r` to force refresh, `1-4` to switch tabs (Overview, Syswatch, Sentinel, Netlab).

## Smoke Test

```bash
make smoke
```

## Troubleshooting

- Receiver returns 422: the event is missing a required field; check `CONTRACT.md`.
- Dashboard says "database unavailable": ensure `make up` ran successfully and `sqlite3 sqlite/pulse.db ".tables"` shows `events`.
- Dashboard queries return no data: check that the stack is running and events have been sent. The SQLite file is read-only from the dashboard; the receiver writes to it.
- Discord alerts are not firing: check `DISCORD_WEBHOOK_URL` in `.env` and receiver logs via `make logs`.
- Remote access to the dashboard: the dashboard is a terminal app and runs on your local machine. To view it remotely, SSH into the box and run `pulse-dashboard` in the SSH terminal.

## Related Repos

- `sentinel` - network IDS
- `netlab` - attack/defense lab
- `syswatch` - system monitor

## License

MIT. See `LICENSE`.
