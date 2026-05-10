"""pulse-platform receiver — accept contract events, persist them, and fan them out."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from receiver.alerting import maybe_alert_discord
from receiver.storage import Storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("receiver")

VALID_SEVERITIES = {"info", "low", "medium", "high", "critical"}
VALID_SOURCES = {"sentinel", "netlab", "syswatch"}


def _get_retention_days() -> int:
    raw_value = os.environ.get("PULSE_RETENTION_DAYS", "")
    if raw_value == "":
        return 30
    return int(raw_value)


def check_bearer_token(request: Request) -> None:
    """Dependency function to check bearer token authentication.
    
    Reads PULSE_RECEIVER_TOKEN from environment. If set, requires requests to include
    Authorization: Bearer <token> header. If not set (or empty), rejects all requests.
    
    Raises HTTPException(401, {"detail": "unauthorized"}) if token is missing, wrong, or empty.
    """
    token_from_env = os.environ.get("PULSE_RECEIVER_TOKEN", "")
    
    # If env var is not set or empty, reject all requests
    if not token_from_env:
        raise HTTPException(status_code=401, detail="unauthorized")    
    # Get Authorization header
    auth_header = request.headers.get("Authorization", "")
    
    # Parse and validate Bearer token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")
    
    token_from_header = auth_header[7:]  # Remove "Bearer " prefix
    
    # Use secrets.compare_digest to prevent timing attacks
    if not secrets.compare_digest(token_from_header, token_from_env):
        raise HTTPException(status_code=401, detail="unauthorized")

class Event(BaseModel):
    schema_version: str
    timestamp: str
    source: str
    source_version: str | None = None
    host: str | None = None
    event_type: str
    severity: str
    event_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


storage: Storage | None = None
retention_task: asyncio.Task[None] | None = None


async def _retention_loop(days: int) -> None:
    while True:
        try:
            if storage is None:
                raise RuntimeError("storage not initialized")
            deleted = await asyncio.to_thread(storage.delete_old_events, days)
            log.info("retention: deleted %d events older than %d days", deleted, days)
            await asyncio.sleep(86400)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("retention job failed")
            await asyncio.sleep(86400)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global storage
    global retention_task
    storage = Storage(
        sqlite_path=os.environ.get("PULSE_SQLITE_DB", "/data/pulse.db"),
        redis_host=os.environ.get("REDIS_HOST", "redis"),
        redis_port=int(os.environ.get("REDIS_PORT", "6379")),
        redis_password=os.environ.get("REDIS_PASSWORD") or None,
    )
    log.info(
        "receiver started; sqlite=%s redis=%s:%s",
        storage.sqlite_path,
        storage.redis_host,
        storage.redis_port,
    )
    retention_days = _get_retention_days()
    retention_task = None
    if retention_days > 0:
        retention_task = asyncio.create_task(_retention_loop(retention_days))

    try:
        yield
    finally:
        if retention_task is not None:
            retention_task.cancel()
            with suppress(asyncio.CancelledError):
                await retention_task
        if storage is not None:
            storage.close()
            storage = None


app = FastAPI(title="pulse-platform receiver", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/events")
async def post_events(request: Request, _token_verified: None = Depends(check_bearer_token)) -> dict[str, Any]:
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"invalid JSON: {exc}") from exc

    raw_events = body if isinstance(body, list) else [body]
    if not raw_events:
        return {"accepted": 0, "rejected": []}

    accepted = 0
    rejected: list[dict[str, str]] = []

    for index, raw in enumerate(raw_events):
        try:
            event = Event.model_validate(raw)
        except ValidationError as exc:
            rejected.append({"index": str(index), "error": str(exc)})
            continue

        if event.severity not in VALID_SEVERITIES:
            rejected.append({"index": str(index), "error": f"invalid severity: {event.severity}"})
            continue

        if event.source not in VALID_SOURCES:
            log.warning("unknown source: %s (event accepted)", event.source)

        received_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        try:
            if storage is None:
                raise RuntimeError("storage not initialized")
            written = storage.write_event(event.model_dump(), received_at=received_at)
        except Exception as exc:
            log.exception("storage.write_event failed")
            rejected.append({"index": str(index), "error": f"storage error: {exc}"})
            continue

        # Only alert if the event was actually written (not a duplicate)
        if written and event.severity in {"high", "critical"}:
            maybe_alert_discord(event.model_dump())

        accepted += 1

    return {"accepted": accepted, "rejected": rejected}