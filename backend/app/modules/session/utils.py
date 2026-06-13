"""Anonymous session cookie handling (contract §7).

A middleware reads the `sl_session` cookie on every request and, if absent,
issues a fresh opaque id and sets the cookie on the way out. Doing this in
middleware (rather than a dependency) means the cookie is set regardless of what
a route returns — a plain dict, a Pydantic model, or a custom JSONResponse.

Routes obtain the current session id with the `get_session_id` dependency.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.core.config import settings

SESSION_COOKIE_NAME = "sl_session"
SESSION_MAX_AGE = 30 * 24 * 60 * 60  # 30 days, in seconds


def set_session_cookie(response: Response, session_id: str) -> None:
    """Attach the `sl_session` cookie with the contract's flags (§7).

    `Secure` is only set in production: over plain HTTP in local development it
    would stop the browser from ever sending the cookie back.
    """
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.ENV == "production",
        path="/",
    )


def register_session_middleware(app: FastAPI) -> None:
    """Issue/track the anonymous session id on every request."""

    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        is_new = session_id is None
        if is_new:
            session_id = uuid4().hex

        # Stash it so the dependency (and thus any route) can read it.
        request.state.session_id = session_id

        response = await call_next(request)

        if is_new:
            set_session_cookie(response, session_id)
        return response


def get_session_id(request: Request) -> str:
    """Dependency: the caller's session id, set by the middleware above."""
    return request.state.session_id
