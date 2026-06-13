"""Catalogue service (M1) — reads the static operation catalogue.

Backs the home screen and operation menu: the full catalogue, and a single
operation's detail with its curated examples.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import OperationNotFoundError
from app.modules.catalogue.models import Category, Operation
from app.modules.catalogue.schemas import (
    CatalogResponse,
    OperationDetailResponse,
)
from app.modules.catalogue.utils import (
    category_to_schema,
    example_to_schema,
    operation_to_schema,
)


class CatalogueService:
    """Read-only access to categories, operations, and their examples."""

    async def get_catalog(self, db: AsyncSession) -> CatalogResponse:
        """Return every category with its operations, ordered for display.

        ``selectinload`` eagerly loads each category's operations in a second
        query, avoiding the implicit lazy loading that async SQLAlchemy forbids.
        """
        stmt = (
            select(Category)
            .options(selectinload(Category.operations))
            .order_by(Category.display_order)
        )
        result = await db.execute(stmt)
        categories = result.scalars().all()

        return CatalogResponse(
            categories=[category_to_schema(category) for category in categories]
        )

    async def get_operation_detail(
        self, slug: str, db: AsyncSession
    ) -> OperationDetailResponse:
        """Return one operation (addressed by slug) plus its examples.

        Raises ``OperationNotFoundError`` (-> 404 ApiError) for an unknown slug.
        """
        stmt = (
            select(Operation)
            .where(Operation.slug == slug)
            .options(
                selectinload(Operation.category),
                selectinload(Operation.examples),
            )
        )
        result = await db.execute(stmt)
        operation = result.scalar_one_or_none()

        if operation is None:
            raise OperationNotFoundError(
                f"No operation exists with slug '{slug}'."
            )

        return OperationDetailResponse(
            operation=operation_to_schema(operation, operation.category.slug),
            examples=[example_to_schema(ex) for ex in operation.examples],
        )
