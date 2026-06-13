from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.modules.catalogue.models import Operation


class Example(Base):
    """A curated input that demonstrates an operation's interesting case (M4)."""

    __tablename__ = "examples"

    example_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    operation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("operations.operation_id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    # Field values keyed by input-field name.
    inputs: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    operation: Mapped[Operation] = relationship(back_populates="examples")
