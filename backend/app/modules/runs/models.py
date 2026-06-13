from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.modules.catalogue.models import Operation


class Run(Base):
    """A recorded execution, scoped to an anonymous session (M5 — History)."""

    __tablename__ = "runs"

    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    operation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("operations.operation_id"), nullable=False
    )
    # Exact inputs submitted by the user.
    input_values: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Computed result object.
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Plain-language account of this specific run (FR-3.3); needed to serve a
    # full RunResult on replay without recomputing.
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    # Cached ordered step list; null for result-level operations.
    trace: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    # Anonymous session id from the HttpOnly cookie; never exposed in responses.
    # Kept as a string: it is an opaque session token, not a surrogate key.
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    operation: Mapped[Operation] = relationship(back_populates="runs")
