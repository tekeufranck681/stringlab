from __future__ import annotations

from typing import Any

from app.core.schemas import BaseSchema


class ValidateRequest(BaseSchema):
    """Body of POST /operations/{slug}/validate (contract §4.3)."""

    inputs: dict[str, Any]


class ValidateResponse(BaseSchema):
    """Success body when inputs are valid."""

    valid: bool
