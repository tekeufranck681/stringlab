import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.database.connection import test_async_connection

# Import every model so SQLAlchemy can resolve string-based relationships (e.g.
# Operation.runs -> "Run") when it configures the mappers on the first query.
import app.database.base  # noqa: F401

logger = logging.getLogger("uvicorn.error")  # Use uvicorn's logger for consistency

ENV = os.getenv("ENV", "development")

# All module endpoints live under this prefix (contract §0 — Base path).
API_V1 = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Server starting in {ENV} mode...")
    # -----------------------
    # DEV + PROD → FULL STARTUP
    # -----------------------
    try:
        await test_async_connection()
        logger.info("Database connection OK")
    except Exception:
        logger.exception("Database connection failed")
        raise

    logger.info("Startup complete")

    yield

    logger.info("Server shutdown complete")


app = FastAPI(lifespan=lifespan, title="StringLab API", version="1.0.0")

# CORS — credentials are required so the browser sends the sl_session cookie
# (contract §7). Origins must be explicit; a wildcard is invalid with credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render every error as the ApiError envelope (contract §1.5, §5).
register_exception_handlers(app)

# Issue/track the anonymous sl_session cookie on every request (contract §7).
from app.modules.session.utils import register_session_middleware

register_session_middleware(app)

# ---------------------------------------------------------------------------
# Module routers — each module owns its endpoints in its own routes.py and is
# registered here under the /api/v1 prefix. Uncomment as each module is built.
# ---------------------------------------------------------------------------
from app.modules.catalogue.routes import router as catalogue_router
from app.modules.computation.routes import router as computation_router
from app.modules.runs.routes import router as runs_router
from app.modules.session.routes import router as session_router
from app.modules.validation.routes import router as validation_router

app.include_router(catalogue_router, prefix=API_V1)
app.include_router(validation_router, prefix=API_V1)
app.include_router(computation_router, prefix=API_V1)
app.include_router(runs_router, prefix=API_V1)
app.include_router(session_router, prefix=API_V1)


# ---------------------------------------------------------------------------
# Routes that belong to no module are defined directly here.
# ---------------------------------------------------------------------------
@app.get("/")
async def welcome():
    return {"message": "Welcome to StringLab API!"}


@app.get("/health")
async def health_check():
    """Top-level liveness probe (ops nicety)."""
    return {"status": "healthy"}


@app.get(f"{API_V1}/health")
async def api_health():
    """Versioned liveness probe (contract §4.8)."""
    return {"status": "ok", "version": "1.0.0"}
