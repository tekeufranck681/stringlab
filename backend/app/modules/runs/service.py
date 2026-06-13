"""Runs service (M5) — persist executions and read a visitor's history.

Records each run against the caller's anonymous session, and serves it back
either as a light history list or a full RunResult (with its cached trace, so a
replay needs no recomputation — contract §4.5, §4.6).
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import OperationNotFoundError, RunNotFoundError
from app.modules.catalogue.models import Operation
from app.modules.catalogue.schemas import Complexity
from app.modules.computation.schemas import ComputationOutcome, Trace
from app.modules.runs.models import Run
from app.modules.runs.schemas import RunListMeta, RunListResponse, RunResult
from app.modules.runs.utils import run_to_list_item


class RunsService:
    async def create_run(
        self,
        slug: str,
        inputs: dict[str, Any],
        outcome: ComputationOutcome,
        session_id: str,
        db: AsyncSession,
    ) -> RunResult:
        """Persist a computed run and return it as a full RunResult (FR-6.1)."""
        operation_id = (
            await db.execute(
                select(Operation.operation_id).where(Operation.slug == slug)
            )
        ).scalar_one_or_none()
        if operation_id is None:
            raise OperationNotFoundError(f"No operation exists with slug '{slug}'.")

        # The trace is cached as JSONB (null for result-level operations) so a
        # later replay needs no recomputation (FR-6.2).
        trace_dict = (
            outcome.trace.model_dump(by_alias=True, exclude_none=True)
            if outcome.trace is not None
            else None
        )

        run = Run(
            operation_id=operation_id,
            input_values=inputs,
            result=outcome.result,
            explanation=outcome.explanation,
            trace=trace_dict,
            session_id=session_id,
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # Reuse the already-built outcome objects; only id and timestamp are new.
        return RunResult(
            run_id=run.run_id,
            operation=slug,
            result=outcome.result,
            explanation=outcome.explanation,
            complexity=outcome.complexity,
            visualization_level=outcome.visualization_level,
            trace=outcome.trace,
            created_at=run.created_at,
        )

    async def get_run(
        self, run_id: uuid.UUID, session_id: str, db: AsyncSession
    ) -> RunResult:
        """Return one full run, including its cached trace (contract §4.6).

        Runs belonging to another session raise ``RunNotFoundError`` exactly like
        a missing id, so we never leak the existence of someone else's run.
        """
        row = (
            await db.execute(
                select(Run, Operation).join(Operation).where(Run.run_id == run_id)
            )
        ).first()

        if row is None:
            raise RunNotFoundError(f"No run exists with id {run_id}.")

        run, operation = row
        if run.session_id != session_id:
            raise RunNotFoundError(f"No run exists with id {run_id}.")

        trace = Trace.model_validate(run.trace) if run.trace is not None else None
        return RunResult(
            run_id=run.run_id,
            operation=operation.slug,
            result=run.result,
            explanation=run.explanation,
            complexity=Complexity(
                time=operation.time_complexity,
                space=operation.space_complexity,
            ),
            visualization_level=operation.visualisation_level,
            trace=trace,
            created_at=run.created_at,
        )

    async def list_runs(
        self,
        session_id: str,
        limit: int,
        offset: int,
        operation_slug: Optional[str],
        db: AsyncSession,
    ) -> RunListResponse:
        """Return this session's runs, newest first, paginated (contract §4.5)."""
        filters = [Run.session_id == session_id]
        if operation_slug is not None:
            filters.append(Operation.slug == operation_slug)

        total = (
            await db.execute(
                select(func.count(Run.run_id)).join(Operation).where(*filters)
            )
        ).scalar_one()

        rows = (
            await db.execute(
                select(Run, Operation.slug)
                .join(Operation)
                .where(*filters)
                .order_by(Run.created_at.desc(), Run.run_id.desc())
                .limit(limit)
                .offset(offset)
            )
        ).all()

        items = [run_to_list_item(run, slug) for run, slug in rows]
        return RunListResponse(
            runs=items,
            meta=RunListMeta(limit=limit, offset=offset, total=total),
        )
