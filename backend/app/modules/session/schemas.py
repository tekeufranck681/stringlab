from __future__ import annotations

from datetime import datetime, timezone

from pydantic import field_serializer

from app.core.schemas import BaseSchema


class SessionInfo(BaseSchema):
    """Lightweight session info (contract §4.7)."""

    session_started: datetime
    run_count: int

    @field_serializer("session_started")
    def _serialize_started(self, dt: datetime) -> str:
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
