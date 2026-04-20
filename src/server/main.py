"""FastAPI application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server.api.projects import router as projects_router
from src.server.config import configure_logging, get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan hooks."""
    log_path = configure_logging()
    settings = get_settings()
    logger.info(
        "Starting backend app_env=%s data_dir=%s port=%s",
        settings.app_env,
        settings.app_data_dir,
        settings.server_port,
    )
    logger.info("Backend log file: %s", log_path)
    yield
    logger.info("Stopping backend")


app = FastAPI(
    title="Vlog Editor API",
    description="AI travel vlog editing system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "data_dir": str(settings.app_data_dir),
        "log_dir": str(settings.app_logs_dir),
        "server_host": settings.server_host,
        "server_port": settings.server_port,
    }
