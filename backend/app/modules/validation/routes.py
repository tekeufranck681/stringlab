"""Validation endpoint (contract §4.3)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.validation.schemas import ValidateRequest, ValidateResponse
from app.modules.validation.service import ValidationService

router = APIRouter(tags=["validation"])
service = ValidationService()


@router.post("/operations/{slug}/validate", response_model=ValidateResponse)
async def validate_operation_inputs(
    slug: str,
    body: ValidateRequest,
    db: AsyncSession = Depends(get_db),
) -> ValidateResponse:
    """Confirm inputs without executing.

    Returns ``{"valid": true}`` when the inputs satisfy the operation's
    InputSpec. Invalid inputs raise ``InputValidationError`` -> a 422 ApiError
    carrying a ``details`` list of field issues. An unknown slug raises 404.
    """
    await service.validate(slug, body.inputs, db)
    return ValidateResponse(valid=True)
