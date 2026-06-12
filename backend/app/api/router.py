"""Aggregate router for the versioned API surface (contract §0 — Base path).

Every endpoint is mounted under ``/api/v1``. As each module's ``routes.py`` is
implemented (catalogue, validation, computation, runs, session), include its
router here.
"""

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["ops"])
async def health() -> dict:
    """Liveness probe (contract §4.8)."""
    return {"status": "ok", "version": "1.0.0"}


# Module routers are included here as they come online, e.g.:
# from app.modules.catalogue.routes import router as catalogue_router
# api_router.include_router(catalogue_router)
