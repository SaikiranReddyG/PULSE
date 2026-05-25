# PHASE 5 Report

## 1) `tmux list-windows -t pulse-ops`

Captured layout from the freshly launched `pulse-ops` session:

```text
0: dashboard* (1 panes) [80x29] [layout c660,80x29,0,0,3] @1 (active)
1: logs (2 panes) [220x50] [layout a481,220x50,0,0{110x50,0,0,4,109x50,111,0,5}] @2
2: syswatch (1 panes) [220x50] [layout ad23,220x50,0,0,6] @3
3: sentinel (1 panes) [220x50] [layout ad24,220x50,0,0,7] @4
4: shell- (1 panes) [220x50] [layout ad25,220x50,0,0,8] @5
```

Deviation: the tmux client rendering in this environment initially showed the shell window as `shell-`. I locked tmux rename behavior in `tmux/launch-pulse-ops.sh` so the window names remain stable when the launcher is used interactively.

## 2) `make status` from `~/codex-workspace/`

```text
=== Pulse Platform ===
NAME                                   IMAGE                                COMMAND                  SERVICE               CREATED       STATUS                 PORTS
pulse-platform-pulse-alert-worker-1    pulse-platform-pulse-alert-worker    "python -m workers.a…"   pulse-alert-worker    2 hours ago   Up 2 hours             
pulse-platform-pulse-digest-worker-1   pulse-platform-pulse-digest-worker   "python -m workers.d…"   pulse-digest-worker   2 hours ago   Up 2 hours             
pulse-platform-receiver-1              pulse-platform-receiver              "sh -c 'uvicorn rece…"   receiver              2 hours ago   Up 2 hours (healthy)   127.0.0.1:8765->8765/tcp
pulse-platform-redis-1                 redis:7.4-alpine                     "docker-entrypoint.s…"   redis                 11 days ago   Up 2 hours (healthy)   127.0.0.1:6379->6379/tcp

=== Sensors ===
● pulse-syswatch.service - Pulse sensor — syswatch system monitor
     Loaded: loaded (/etc/systemd/system/pulse-syswatch.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-05-25 13:52:11 CEST; 1h 53min ago
   Main PID: 2026 (syswatch)
     CGroup: /system.slice/pulse-syswatch.service
May 25 15:45:59 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:00 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:00 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:01 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:01 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:02 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:02 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:03 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:03 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
May 25 15:46:04 pop-os pulse-syswatch[2026]: syswatch: dropping HTTP batch due to client error 400
● pulse-sentinel.service - Pulse sensor — sentinel network IDS
     Loaded: loaded (/etc/systemd/system/pulse-sentinel.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-05-25 13:52:11 CEST; 1h 53min ago
   Main PID: 2022 (sentinel)
     CGroup: /system.slice/pulse-sentinel.service
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.114.22", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:16:18.791+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.113.22", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:17:02.242+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.113.22", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:17:30.492+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.113.21", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:17:42.733+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.113.22", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:19:49.603+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "13.89.179.13", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:20:01.563+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.113.21", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:20:19.370+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.113.22", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:20:33.458+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:SSH brute force", "dst_ip": "140.82.121.3", "message": "Possible SSH brute force from 10.66.67.153 (10 attempts in 60s)", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:22:22.088+02:00"}
May 25 15:25:54 pop-os pulse-sentinel[2022]: {"event_type": "sentinel.alert", "host": "pop-os", "payload": {"detection_type": "RULE:HTTPS flood", "dst_ip": "140.82.114.22", "message": "HTTPS flood from 10.66.67.153 — 200 connections in 10s", "severity": "high", "src_ip": "10.66.67.153"}, "schema_version": "1.0", "severity": "high", "source": "sentinel", "source_version": "0.1.0", "timestamp": "2026-05-25T15:25:41.416+02:00"}
```

## 3) `make -n up` and `make -n down`

```text
echo "→ Starting Pulse platform..."
cd /home/reddy/codex-workspace/codex-platform && docker compose up -d --build
echo "→ Starting sensors..."
sudo systemctl start pulse-syswatch.service pulse-sentinel.service
echo "✓ Stack up"

---
echo "→ Stopping sensors..."
sudo systemctl stop pulse-syswatch.service pulse-sentinel.service
echo "→ Stopping Pulse platform..."
cd /home/reddy/codex-workspace/codex-platform && docker compose down
echo "✓ Stack down"
```

## 4) `pulse` alias confirmation

```text
pulse is an alias for ~/codex-workspace/codex-platform/tmux/launch-pulse-ops.sh
```

## 5) Deviations

- The tmux client in this environment renders the shell window with an auto-renamed `shell-` label in the captured listing; the launcher now disables tmux auto-rename so the window name remains stable during normal use.
- `~/codex-workspace/Makefile` was created as a workspace-level helper and is not part of the `codex-platform` Git repository/PR.
