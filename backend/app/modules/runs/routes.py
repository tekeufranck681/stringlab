"""Run history endpoints (contract §4.5, §4.6)."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.runs.schemas import RunListResponse
from app.modules.runs.service import RunsService
from app.modules.runs.utils import run_result_response
from app.modules.session.utils import get_session_id

router = APIRouter(tags=["runs"])
service = RunsService()


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    operation: Optional[str] = Query(None, description="Filter by operation slug."),
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
) -> RunListResponse:
    """Recent runs for the caller's session, paginated (FR-6.3)."""
    return await service.list_runs(session_id, limit, offset, operation, db)


@router.get("/runs/{run_id}")
async def get_run(
    run_id: uuid.UUID,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """One full run with its cached trace (FR-6.2); 404 if not in this session."""
    run_result = await service.get_run(run_id, session_id, db)
    return run_result_response(run_result)
