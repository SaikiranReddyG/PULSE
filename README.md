# codex-platform

`codex-platform` is a single-host SOC integration stack. It receives codex-contract JSON events from three sibling tools, `sentinel` (network IDS), `netlab` (attack/defense lab), and `syswatch` (system monitor), then persists, alerts on, and visualizes those events.

It is not a multi-host SIEM, not a managed service, and not a fleet manager. It runs on one Linux box. The security tools themselves live in separate repos and emit events to this platform's HTTP receiver.

## Services

The stack is four containers:

| Service | Purpose |
|---|---|
| `receiver` | HTTP API that accepts contract events, validates them, writes SQLite, and fans out to Redis Streams and Discord alerts |
| `redis` | Live event tail via Redis Streams |
| `grafana` | Dashboards built from SQLite |
| `n8n` | Optional profile for future workflow automation |

The legacy bus has been removed. The integration shape is HTTP POST.

## Quick Start

```bash
git clone <repo-url> codex-platform && cd codex-platform
cp .env.example .env
# edit .env to set passwords and (optionally) DISCORD_WEBHOOK_URL
make up

# Verify the receiver is up
curl http://127.0.0.1:8765/health
# → {"status":"ok"}

# Open Grafana
xdg-open http://127.0.0.1:3000

# Stop
make down
```

## How Tools Connect

Each codex tool supports an `http_post` output destination. Point it at the receiver endpoint:

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
           ┌─────────┐
           │ Grafana │  dashboards reading SQLite
           └─────────┘

Optional: Discord webhook on high/critical events
```

## Configuration

Copy `.env.example` to `.env` and edit the passwords and any optional alerting settings. The receiver, Redis, and Grafana ports are localhost-only by default.

## Smoke Test

```bash
make smoke
```

## Troubleshooting

- Receiver returns 422: the event is missing a required field; check `CONTRACT.md`.
- Grafana shows no data: ensure `make up` ran successfully and `sqlite3 sqlite/codex.db ".tables"` shows `events`.
- Discord alerts are not firing: check `DISCORD_WEBHOOK_URL` in `.env` and receiver logs via `make logs`.

## Related Repos

- `sentinel` - network IDS
- `netlab` - attack/defense lab
- `syswatch` - system monitor

## License

MIT. See `LICENSE`.
