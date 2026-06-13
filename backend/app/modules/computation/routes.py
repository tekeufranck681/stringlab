"""The core execution endpoint (contract §4.4).

`POST /operations/{slug}/run` is the single execution path: validate -> compute
-> record -> respond. Validation and computation are M3 (stateless); recording
is M5; the session cookie is issued by the session middleware.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.computation.schemas import RunRequest
from app.modules.computation.service import ComputationService
from app.modules.runs.service import RunsService
from app.modules.runs.utils import run_result_response
from app.modules.session.utils import get_session_id

router = APIRouter(tags=["computation"])
computation_service = ComputationService()
runs_service = RunsService()


@router.post("/operations/{slug}/run")
async def run_operation(
    slug: str,
    body: RunRequest,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Execute an operation and record the run, returning a full RunResult.

    Raises 404 for an unknown slug and 422 for invalid inputs (both as ApiError
    envelopes). The response keeps ``trace`` as ``null`` for result-level
    operations (§1.4).
    """
    outcome = await computation_service.compute(slug, body.inputs, db)
    run_result = await runs_service.create_run(slug, body.inputs, outcome, session_id, db)
    return run_result_response(run_result)
