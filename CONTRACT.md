# pulse-platform Receiver Contract

## Purpose

`pulse-platform` consumes pulse-contract events. This document describes the receiver-side contract for `POST /events`. The sender-side contract lives in each tool's own `CONTRACT.md`.

## Event Schema Accepted By `POST /events`

| Field | Required | Type | Notes |
|---|---|---|---|
| `schema_version` | yes | string | Currently `"1.0"` |
| `timestamp` | yes | string | RFC 3339, millisecond precision, with offset |
| `source` | yes | string | `sentinel`, `netlab`, or `syswatch`; others are accepted with a warning |
| `source_version` | no | string | Tool semver, for example `"0.1.0"` |
| `host` | no | string | Hostname of the emitter |
| `event_type` | yes | string | Dotted namespace, for example `sentinel.alert` |
| `severity` | yes | string | One of `info`, `low`, `medium`, `high`, `critical` |
| `payload` | yes | object | Free-form per source |

## Endpoint Behavior

- `POST /events` accepts a single event object or a JSON array of event objects.
- The receiver returns `{"accepted": N, "rejected": [...]}` with HTTP 200.
- HTTP 400 is returned only for malformed JSON.
- Per-event validation errors are reported in the `rejected` array and do not fail the whole batch.
- Idempotency is not provided in v0.1. Retries may create duplicate rows.

## Storage And Downstream

- All accepted events are written to SQLite in the `events` table.
- Events are also `XADD`-ed to a Redis Stream named `pulse:events:<source>`.
- Redis failures are best effort and do not block SQLite writes.
- Events with `severity` in `{high, critical}` trigger a Discord webhook when configured.

## What This Is Not

- Not idempotent.
- Not authenticated.
- Not transactional across SQLite and Redis.
- Not exposed beyond localhost by default.