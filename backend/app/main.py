import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.database.connection import test_async_connection

logger = logging.getLogger("uvicorn.error")  # Use uvicorn's logger for consistency

ENV = os.getenv("ENV", "development")


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

# Versioned API surface (contract §0 — all endpoints under /api/v1).
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def welcome():
    return {"message": "Welcome to StringLab API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
