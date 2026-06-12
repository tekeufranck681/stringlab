from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.modules.catalogue.models import Operation


class Run(Base):
    """A recorded execution, scoped to an anonymous session (M5 — History)."""

    __tablename__ = "runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.operation_id"), nullable=False
    )
    # Exact inputs submitted by the user.
    input_values: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Computed result object.
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Cached ordered step list; null for result-level operations.
    trace: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # Anonymous session id from the HttpOnly cookie; never exposed in responses.
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    operation: Mapped[Operation] = relationship(back_populates="runs")
