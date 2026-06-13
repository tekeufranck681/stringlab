from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import field_serializer

from app.core.schemas import BaseSchema
from app.modules.catalogue.schemas import Complexity, VisualizationLevel
from app.modules.computation.schemas import Trace


def _iso_z(dt: datetime) -> str:
    """ISO 8601 UTC with a trailing Z (contract §0 — Timestamps)."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RunResult(BaseSchema):
    """The response of an execution (contract §1.4)."""

    run_id: uuid.UUID
    operation: str
    result: dict[str, Any]
    explanation: str
    complexity: Complexity
    visualization_level: VisualizationLevel
    # Ordered steps for step_log/full; null for result-level operations.
    trace: Optional[Trace] = None
    created_at: datetime

    @field_serializer("created_at")
    def _serialize_created_at(self, dt: datetime) -> str:
        return _iso_z(dt)


class RunListItem(BaseSchema):
    """A lightweight history entry (contract §4.5)."""

    run_id: uuid.UUID
    operation: str
    inputs: dict[str, Any]
    result_summary: str
    created_at: datetime

    @field_serializer("created_at")
    def _serialize_created_at(self, dt: datetime) -> str:
        return _iso_z(dt)


class RunListMeta(BaseSchema):
    limit: int
    offset: int
    total: int


class RunListResponse(BaseSchema):
    runs: list[RunListItem]
    meta: RunListMeta
