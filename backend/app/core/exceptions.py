from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.schemas import BaseSchema


# ---------------------------------------------------------------------------
# Wire shapes (contract §1.5) — the ApiError envelope every error responds with.
# ---------------------------------------------------------------------------
class FieldIssue(BaseSchema):
    field: str
    issue: str
    message: str


class _ErrorBody(BaseSchema):
    code: str
    message: str
    details: Optional[list[FieldIssue]] = None


class ApiError(BaseSchema):
    error: _ErrorBody


# ---------------------------------------------------------------------------
# Application exceptions — raise these from services/routes; the registered
# handlers translate them into the ApiError envelope with the right status.
# ---------------------------------------------------------------------------
class AppException(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    default_message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[list[FieldIssue]] = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)


class OperationNotFoundError(AppException):
    status_code = 404
    code = "OPERATION_NOT_FOUND"
    default_message = "The requested operation does not exist."


class RunNotFoundError(AppException):
    status_code = 404
    code = "RUN_NOT_FOUND"
    default_message = "The requested run does not exist."


class InputValidationError(AppException):
    status_code = 422
    code = "VALIDATION_ERROR"
    default_message = "One or more inputs are invalid."


def _envelope(code: str, message: str, details: Optional[list[dict]] = None) -> dict:
    body: dict = {"code": code, "message": message}
    if details:
        body["details"] = details
    return {"error": body}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that render every error as the ApiError envelope."""

    @app.exception_handler(AppException)
    async def _app_exception(request: Request, exc: AppException) -> JSONResponse:
        details = (
            [i.model_dump(by_alias=True) for i in exc.details] if exc.details else None
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, details),
        )

    @app.exception_handler(RequestValidationError)
    async def _request_validation(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = []
        for err in exc.errors():
            loc = err.get("loc", [])
            field = str(loc[-1]) if loc else "body"
            details.append(
                {
                    "field": field,
                    "issue": "INVALID",
                    "message": err.get("msg", "Invalid value."),
                }
            )
        return JSONResponse(
            status_code=422,
            content=_envelope(
                "VALIDATION_ERROR", "One or more inputs are invalid.", details
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(code, str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_envelope(
                "INTERNAL_ERROR", "An unexpected server error occurred."
            ),
        )
