"""Computation service (M3) — validate, then run an operation.

Orchestrates the stateless pipeline: validate the inputs (reusing M2), load the
operation's display metadata, and execute the engine to produce a result,
explanation, and (for step_log/full operations) a trace. Persistence and the
session cookie are layered on by the runs module (M5) that wraps this output.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import OperationNotFoundError
from app.modules.catalogue.models import Operation
from app.modules.catalogue.schemas import Complexity
from app.modules.computation.schemas import ComputationOutcome
from app.modules.computation.utils import run_operation
from app.modules.validation.service import ValidationService


class ComputationService:
    """Runs an operation end to end, returning the engine outcome."""

    def __init__(self) -> None:
        self.validation = ValidationService()

    async def compute(
        self, slug: str, inputs: dict[str, Any], db: AsyncSession
    ) -> ComputationOutcome:
        """Validate and execute `slug` against `inputs`.

        Raises ``OperationNotFoundError`` (404) for an unknown slug and
        ``InputValidationError`` (422) for invalid inputs. A result-level
        operation returns ``trace = None``.
        """
        # 1. Validate inputs against the operation's InputSpec (M2, authority).
        await self.validation.validate(slug, inputs, db)

        # 2. Load the operation for its complexity and visualisation level.
        operation = (
            await db.execute(select(Operation).where(Operation.slug == slug))
        ).scalar_one_or_none()
        if operation is None:
            raise OperationNotFoundError(f"No operation exists with slug '{slug}'.")

        # 3. Run the engine (inputs are now known valid).
        result, explanation, trace = run_operation(slug, inputs)

        return ComputationOutcome(
            result=result,
            explanation=explanation,
            complexity=Complexity(
                time=operation.time_complexity,
                space=operation.space_complexity,
            ),
            visualization_level=operation.visualisation_level,
            trace=trace,
        )
