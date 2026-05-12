# IDEAS — pulse-platform v0.2 and beyond

## v0.2 dashboard backlog

- **Live tail mode**: full-screen scrolling event view, filter by severity/source.
- **Per-scenario timeline view**: when a netlab row is selected, drill in to a time-axis view of that scenario's events.
- **Topology panel**: ASCII diagram of ARP-spoof / MITM scenarios showing attacker / victim / gateway roles.
- **Top-talkers**: ranked source/dest IPs from sentinel alerts.
- **Anomaly markers on syswatch sparklines**: red dot when syswatch.anomaly fires.
- **Alert sound or system notification** on critical events.
- **Theme variants**: light mode, high-contrast mode.
- **Remote dashboard**: an HTTP variant of the dashboard for viewing in a browser when SSH isn't available.

## Stack additions (deferred to v0.3+)

- Mosquitto MQTT bus, only if tools ever need fleet or multi-host comms.
- Threat intel enrichment: `load_intel.py` and `threat-intel/intel.yaml` were deleted in v0.1; rebuild as a sidecar service that reads from events and writes enriched rows.
- Prometheus exporter for stack metrics such as events per second and Redis stream depth.
- Loki for log aggregation across stack services.
- Wazuh-style HIDS alerting integration.
## Receiver improvements

- Idempotency keys to deduplicate retries.
- Bearer token auth for `/events` in non-localhost deployments.
- Rate limiting per source.
- Schema version negotiation so tools can discover supported schema versions at startup.
- Batched Redis `XADD`.

## Receiver improvements

- Idempotency keys to deduplicate retries.
- Bearer token auth for `/events` in non-localhost deployments.
- Rate limiting per source.
- Schema version negotiation so tools can discover supported schema versions at startup.
- Batched Redis `XADD`.

## Dashboards And Visualization

- Per-source dashboards for sentinel, netlab, and syswatch.
- A topology panel with last-seen time for each emitter.
- Time-range and source filters as Grafana template variables.
- Recurring report export as PDF.

## Deployment

- `docker-compose.override.yml.example` for LAN-bind config.
- Vagrantfile for the old two-machine variant.
- Helm chart for Kubernetes deployment.
- Single-binary build with embedded SQLite and HTTP server.

## Demo Path

- `make demo` with scripted sample events and a repeatable dashboard walkthrough.
- Sample event fixtures for offline demos.