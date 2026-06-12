from __future__ import annotations

from typing import Any, Literal, Optional, Union

from app.core.schemas import BaseSchema


# ---------------------------------------------------------------------------
# Run request body (contract §4.4).
# ---------------------------------------------------------------------------
class RunRequest(BaseSchema):
    inputs: dict[str, Any]


# ---------------------------------------------------------------------------
# The trace & step schema (contract §3) — the heart of the visualisation.
# Backend never sends colours; `role` carries meaning and the frontend maps it.
# ---------------------------------------------------------------------------
TraceAction = Literal[
    # generic
    "init", "done",
    # sequence
    "compare", "match", "mismatch", "expand",
    # search
    "shift", "jump", "found",
    # matrix
    "fill_cell", "choose", "trace_back",
]
TraceFamily = Literal["sequence", "search", "matrix"]
HighlightTarget = Literal["text", "pattern", "cell"]
HighlightRole = Literal["active", "compare", "match", "mismatch", "path", "result"]


class CellRef(BaseSchema):
    row: int
    col: int


class Highlight(BaseSchema):
    target: HighlightTarget
    index: Optional[int] = None  # single position (text/pattern)
    range: Optional[tuple[int, int]] = None  # inclusive span (text/pattern)
    cell: Optional[CellRef] = None  # matrix
    role: HighlightRole


# State variants (contract §3) — one per visualiser family.
class SequenceState(BaseSchema):
    left: int
    right: int
    window: Optional[tuple[int, int]] = None


class SearchState(BaseSchema):
    text_index: int
    pattern_index: int
    shift: int
    comparisons: int
    failure_table: Optional[list[int]] = None


class MatrixState(BaseSchema):
    cell: CellRef
    value: int
    choice: Optional[Literal["match", "insert", "delete", "substitute"]] = None


TraceState = Union[SearchState, MatrixState, SequenceState]


class TraceAxes(BaseSchema):
    row_label: Optional[str] = None
    col_label: Optional[str] = None


class TraceDimensions(BaseSchema):
    rows: int
    cols: int


class TraceMeta(BaseSchema):
    total_steps: int
    family: TraceFamily
    axes: Optional[TraceAxes] = None  # matrix: the two strings
    dimensions: Optional[TraceDimensions] = None  # matrix


class TraceStep(BaseSchema):
    index: int  # 0-based, sequential
    action: TraceAction
    message: str  # human narration for the step log
    state: Optional[TraceState] = None
    highlights: Optional[list[Highlight]] = None


class Trace(BaseSchema):
    steps: list[TraceStep]
    meta: TraceMeta
