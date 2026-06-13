from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.modules.examples.models import Example
    from app.modules.runs.models import Run


class Category(Base):
    """A grouping of operations on the home screen (M1 — Catalogue)."""

    __tablename__ = "categories"

    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    operations: Mapped[list[Operation]] = relationship(
        back_populates="category",
        order_by="Operation.slug",
        cascade="all, delete-orphan",
    )


class Operation(Base):
    """A single string operation and everything needed to render and run it."""

    __tablename__ = "operations"

    operation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.category_id"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    # Field definitions for the generic input panel (contract §2).
    input_spec: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    time_complexity: Mapped[str] = mapped_column(String(40), nullable=False)
    space_complexity: Mapped[str] = mapped_column(String(40), nullable=False)
    visualisation_level: Mapped[str] = mapped_column(String(20), nullable=False)

    category: Mapped[Category] = relationship(back_populates="operations")
    examples: Mapped[list[Example]] = relationship(
        back_populates="operation",
        order_by="Example.display_order",
        cascade="all, delete-orphan",
    )
    runs: Mapped[list[Run]] = relationship(back_populates="operation")
