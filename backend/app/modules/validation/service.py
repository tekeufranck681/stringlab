"""Validation service (M2) — server-side authority over operation inputs.

Loads an operation's input specification and validates submitted inputs against
it. Holds no tables of its own; it reads the catalogue (contract §4.3, §6) and
is reused by the run pipeline so the same rules apply everywhere.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InputValidationError, OperationNotFoundError
from app.modules.catalogue.models import Operation
from app.modules.catalogue.schemas import InputSpec
from app.modules.validation.utils import validate_inputs


class ValidationService:
    """Validates inputs for an operation, by slug, against its InputSpec."""

    async def _load_spec(self, slug: str, db: AsyncSession) -> InputSpec:
        """Fetch just the input_spec for `slug`, or raise if the slug is unknown."""
        stmt = select(Operation.input_spec).where(Operation.slug == slug)
        result = await db.execute(stmt)
        raw_spec = result.scalar_one_or_none()

        if raw_spec is None:
            raise OperationNotFoundError(
                f"No operation exists with slug '{slug}'."
            )
        return InputSpec.model_validate(raw_spec)

    async def validate(
        self, slug: str, inputs: dict[str, Any], db: AsyncSession
    ) -> None:
        """Validate `inputs`; raise InputValidationError (422) if anything fails.

        Returns nothing on success. The run pipeline calls this before computing,
        so a successful return is the signal that the inputs are safe to use.
        """
        spec = await self._load_spec(slug, db)
        issues = validate_inputs(spec, inputs)
        if issues:
            raise InputValidationError(details=issues)
