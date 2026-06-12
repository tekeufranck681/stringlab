from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI

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


app = FastAPI(lifespan=lifespan, title="LinkDem API", version="1.0")


@app.get("/")
async def welcome():
    return {"message": "Welcome to StringLab API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}