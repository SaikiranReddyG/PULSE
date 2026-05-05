.PHONY: up down logs smoke clean test dashboard help

DOCKER_COMPOSE := docker compose

help:
	@echo "codex-platform Makefile targets:"
	@echo "  make up      - start the stack (receiver + redis)"
	@echo "  make down    - stop the stack, keep volumes"
	@echo "  make logs    - tail logs from all services"
	@echo "  make smoke   - run end-to-end smoke test"
	@echo "  make test    - run receiver unit tests"
	@echo "  make clean   - stop stack and delete volumes (DESTRUCTIVE)"
	@echo "  make dashboard - launch the terminal dashboard"

up:
	@test -f .env || (echo "ERROR: .env not found. Copy .env.example to .env first." && exit 1)
	mkdir -p sqlite redis-data
	@if [ ! -f sqlite/codex.db ]; then \
	  echo "Initializing SQLite schema..."; \
	  sqlite3 sqlite/codex.db < sqlite/schema.sql; \
	fi
	$(DOCKER_COMPOSE) up -d --build
	@echo ""
	@echo "Stack up. Receiver: http://127.0.0.1:8765"
	@echo "Run 'codex-dashboard' (or 'make dashboard') to view the terminal dashboard."

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f --tail=200

smoke:
	bash tests/smoke.sh

test:
	cd receiver && python -m pytest ../tests/ -v
dashboard:
	@command -v codex-dashboard >/dev/null 2>&1 || (echo "Installing dashboard from venv..." && cd dashboard && .venv/bin/pip install -q -e . && cd ..)
	dashboard/.venv/bin/codex-dashboard

clean:
	$(DOCKER_COMPOSE) down -v
	rm -rf sqlite/codex.db sqlite/codex.db-journal sqlite/codex.db-wal sqlite/codex.db-shm
	rm -rf redislite/codex.db-journal sqlite/codex.db-wal sqlite/codex.db-shm
	rm -rf redis-data grafana-data n8n-data