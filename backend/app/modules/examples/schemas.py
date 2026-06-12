from __future__ import annotations

from typing import Any

from app.core.schemas import BaseSchema


class ExampleSchema(BaseSchema):
    """A curated example input for an operation (contract §1.3)."""

    id: int
    label: str
    # Field values keyed by input-field name.
    inputs: dict[str, Any]
    note: str
