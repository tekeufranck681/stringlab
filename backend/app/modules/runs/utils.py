"""Helpers for the runs module: ORM -> schema mapping and response shaping."""

from __future__ import annotations

from fastapi.responses import JSONResponse

from app.modules.runs.models import Run
from app.modules.runs.schemas import RunListItem, RunResult


def run_to_list_item(run: Run, operation_slug: str) -> RunListItem:
    """Map a Run row to a lightweight history entry (contract §4.5).

    The stored per-run `explanation` doubles as the short `resultSummary`, so
    the list stays light without recomputing or carrying the full result/trace.
    """
    return RunListItem(
        run_id=run.run_id,
        operation=operation_slug,
        inputs=run.input_values,
        result_summary=run.explanation,
        created_at=run.created_at,
    )


def run_result_response(run_result: RunResult) -> JSONResponse:
    """Serialise a RunResult, omitting absent optionals but keeping `trace`.

    Contract §0 omits absent optional fields, but §1.4 requires `trace` to be
    present as ``null`` for result-level operations (the frontend's type is
    ``Trace | null``). ``exclude_none`` handles the former; we restore the
    explicit ``trace: null`` for the latter.
    """
    data = run_result.model_dump(by_alias=True, exclude_none=True, mode="json")
    if "trace" not in data:
        data["trace"] = None
    return JSONResponse(content=data)
