#!/usr/bin/env bash
# tests/smoke.sh — end-to-end smoke test for codex-platform v0.1.
#
# What it does:
#   1. Brings the stack up.
#   2. Waits for the receiver to be healthy.
#   3. POSTs a sample event from each of the three sources.
#   4. Queries SQLite to confirm the events landed.
#   5. Tears the stack down.
#
# This script does NOT depend on the actual sentinel/netlab/syswatch binaries.
# It crafts contract events directly so the platform wiring can be verified.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

cleanup() {
  make down >/dev/null 2>&1 || true
}
trap cleanup EXIT

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Copy .env.example to .env first."
  exit 1
fi

echo "==== Bringing up stack ===="
rm -f sqlite/codex.db sqlite/codex.db-journal sqlite/codex.db-wal sqlite/codex.db-shm
make up

echo "==== Waiting for receiver to be healthy ===="
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -sf http://127.0.0.1:8765/health >/dev/null 2>&1; then
    echo "[+] Receiver healthy after ${i} retries"
    break
  fi
  if [[ $i -eq 10 ]]; then
    echo "[!] FAIL: receiver never became healthy"
    exit 1
  fi
  sleep 2
done

echo "==== POSTing sample events ===="

curl -sf -X POST http://127.0.0.1:8765/events \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "1.0",
    "timestamp": "2026-05-01T12:00:00.000+02:00",
    "source": "sentinel",
    "source_version": "0.1.0",
    "host": "smoke-test",
    "event_type": "sentinel.lifecycle.started",
    "severity": "info",
    "payload": {"interface": "lo"}
  }' | tee /tmp/codex-smoke-1.json
echo

curl -sf -X POST http://127.0.0.1:8765/events \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "1.0",
    "timestamp": "2026-05-01T12:00:01.000+02:00",
    "source": "netlab",
    "source_version": "0.1.0",
    "host": "smoke-test",
    "event_type": "netlab.scenario.started",
    "severity": "info",
    "payload": {"scenario": "arp_spoof"}
  }' | tee /tmp/codex-smoke-2.json
echo

curl -sf -X POST http://127.0.0.1:8765/events \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "1.0",
    "timestamp": "2026-05-01T12:00:02.000+02:00",
    "source": "syswatch",
    "source_version": "0.1.0",
    "host": "smoke-test",
    "event_type": "syswatch.metrics",
    "severity": "info",
    "payload": {"cpu_percent": 42.5, "mem_percent": 61.0}
  }' | tee /tmp/codex-smoke-3.json
echo

curl -sf -X POST http://127.0.0.1:8765/events \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "1.0",
    "timestamp": "2026-05-01T12:00:03.000+02:00",
    "source": "sentinel",
    "source_version": "0.1.0",
    "host": "smoke-test",
    "event_type": "sentinel.alert",
    "severity": "high",
    "payload": {"detection_type": "PORT_SCAN", "src_ip": "1.2.3.4", "dst_ip": "5.6.7.8", "message": "smoke test alert"}
  }' | tee /tmp/codex-smoke-4.json
echo

curl -sf -X POST http://127.0.0.1:8765/events \
  -H "Content-Type: application/json" \
  -d '{"schema_version": "1.0"}' | tee /tmp/codex-smoke-5.json
echo

echo "==== Querying SQLite to verify persistence ===="
EVENT_COUNT=$(sqlite3 sqlite/codex.db "SELECT COUNT(*) FROM events WHERE host = 'smoke-test'")
if [[ "${EVENT_COUNT}" -lt 4 ]]; then
  echo "[!] FAIL: expected at least 4 events with host='smoke-test', got ${EVENT_COUNT}"
  sqlite3 sqlite/codex.db "SELECT id, source, event_type, severity FROM events WHERE host = 'smoke-test'"
  exit 1
fi
echo "[+] Found ${EVENT_COUNT} smoke-test events in SQLite"

echo "==== Verifying source distribution ===="
SOURCES=$(sqlite3 sqlite/codex.db "SELECT DISTINCT source FROM events WHERE host = 'smoke-test' ORDER BY source")
EXPECTED=$'netlab\nsentinel\nsyswatch'
if [[ "${SOURCES}" != "${EXPECTED}" ]]; then
  echo "[!] FAIL: expected sources netlab/sentinel/syswatch, got:"
  echo "${SOURCES}"
  exit 1
fi
echo "[+] All three sources present: sentinel, netlab, syswatch"

echo "==== Tearing down stack ===="
make down

echo
echo "[+] smoke test passed"