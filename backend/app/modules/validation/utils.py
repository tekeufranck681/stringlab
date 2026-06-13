"""Pure input-validation logic (contract §6).

`validate_inputs` checks a submitted `inputs` object against an operation's
`InputSpec` and returns a list of `FieldIssue`s — empty when everything is
valid. It is deliberately free of any database or framework concern so it can be
reused by both the `/validate` endpoint and the `/run` pipeline, and unit-tested
in isolation.

Each constraint maps to one machine-readable `issue` code:

    required               -> REQUIRED
    maxLength / minLength  -> TOO_LONG / TOO_SHORT
    allowedAlphabet        -> INVALID_ALPHABET
    min / max (integer)    -> OUT_OF_RANGE
    (integer parse)        -> NOT_AN_INTEGER
    options (select)       -> INVALID_OPTION
"""

from __future__ import annotations

import re
from typing import Any, Optional

from app.core.exceptions import FieldIssue
from app.modules.catalogue.schemas import InputField, InputSpec


def _is_present(value: Any) -> bool:
    """A value counts as supplied unless it is missing or an empty string.

    An empty required field is treated as absent (contract §6: "empty required
    input is rejected").
    """
    return value is not None and value != ""


def _parse_int(value: Any) -> Optional[int]:
    """Return `value` as an int, or None if it cannot be one.

    Booleans are rejected even though `bool` is a subclass of `int` — a checkbox
    value is not a number. Numeric strings like "12" are accepted.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _validate_string(field: InputField, value: Any) -> list[FieldIssue]:
    issues: list[FieldIssue] = []
    text = value if isinstance(value, str) else str(value)
    c = field.constraints

    if c is not None:
        if c.min_length is not None and len(text) < c.min_length:
            issues.append(FieldIssue(
                field=field.name, issue="TOO_SHORT",
                message=f"{field.label} must be at least {c.min_length} characters.",
            ))
        if c.max_length is not None and len(text) > c.max_length:
            issues.append(FieldIssue(
                field=field.name, issue="TOO_LONG",
                message=f"{field.label} must be at most {c.max_length} characters.",
            ))
        if c.allowed_alphabet and not re.fullmatch(f"[{c.allowed_alphabet}]*", text):
            issues.append(FieldIssue(
                field=field.name, issue="INVALID_ALPHABET",
                message=f"{field.label} contains characters outside the allowed set.",
            ))
    return issues


def _validate_integer(field: InputField, value: Any) -> list[FieldIssue]:
    number = _parse_int(value)
    if number is None:
        return [FieldIssue(
            field=field.name, issue="NOT_AN_INTEGER",
            message=f"{field.label} must be a whole number.",
        )]

    issues: list[FieldIssue] = []
    c = field.constraints
    if c is not None and (c.min is not None or c.max is not None):
        below = c.min is not None and number < c.min
        above = c.max is not None and number > c.max
        if below or above:
            issues.append(FieldIssue(
                field=field.name, issue="OUT_OF_RANGE",
                message=f"{field.label} must be between {c.min} and {c.max}.",
            ))
    return issues


def _validate_select(field: InputField, value: Any) -> list[FieldIssue]:
    options = field.constraints.options if field.constraints else None
    allowed = {option.value for option in (options or [])}
    if str(value) not in allowed:
        return [FieldIssue(
            field=field.name, issue="INVALID_OPTION",
            message=f"{field.label} must be one of: {', '.join(sorted(allowed))}.",
        )]
    return []


def validate_inputs(spec: InputSpec, inputs: dict[str, Any]) -> list[FieldIssue]:
    """Validate `inputs` against `spec`; return all issues found (possibly empty).

    Fields are checked independently so the user sees every problem at once
    rather than one at a time. Inputs not named in the spec are ignored.
    """
    issues: list[FieldIssue] = []

    for field in spec.fields:
        value = inputs.get(field.name)

        if not _is_present(value):
            if field.required:
                issues.append(FieldIssue(
                    field=field.name, issue="REQUIRED",
                    message=f"{field.label} is required.",
                ))
            # Absent optional field: nothing more to check.
            continue

        if field.type == "string":
            issues.extend(_validate_string(field, value))
        elif field.type == "integer":
            issues.extend(_validate_integer(field, value))
        elif field.type == "select":
            issues.extend(_validate_select(field, value))
        # "boolean" has no constraints to enforce; any present value is accepted.

    return issues
