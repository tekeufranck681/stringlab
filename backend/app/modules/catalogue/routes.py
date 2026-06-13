"""Catalogue endpoints (contract §4.1, §4.2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.modules.catalogue.schemas import (
    CatalogResponse,
    OperationDetailResponse,
)
from app.modules.catalogue.service import CatalogueService

router = APIRouter(tags=["catalogue"])
service = CatalogueService()


# response_model_exclude_none drops absent optional fields rather than sending
# them as null (contract §0). Safe for the catalogue, which has no semantically
# meaningful nulls (unlike RunResult.trace, which must stay null when present).
@router.get(
    "/catalog", response_model=CatalogResponse, response_model_exclude_none=True
)
async def get_catalog(db: AsyncSession = Depends(get_db)) -> CatalogResponse:
    """Categories with their operations — powers the home screen (FR-1)."""
    return await service.get_catalog(db)


@router.get(
    "/operations/{slug}",
    response_model=OperationDetailResponse,
    response_model_exclude_none=True,
)
async def get_operation(
    slug: str, db: AsyncSession = Depends(get_db)
) -> OperationDetailResponse:
    """One operation's full detail plus its curated examples (FR-1.3, FR-4)."""
    return await service.get_operation_detail(slug, db)
