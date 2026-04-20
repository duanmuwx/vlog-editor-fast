"""Runtime configuration for the backend service."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.server.storage.database import get_app_data_dir, get_app_logs_dir


@dataclass(frozen=True)
class Settings:
    """Runtime settings resolved from environment variables."""

    app_env: str
    app_data_dir: Path
    app_logs_dir: Path
    server_host: str
    server_port: int
    log_level: str
    kimi_api_key: str | None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Resolve runtime settings from environment variables."""
    app_data_dir = get_app_data_dir(create=True)
    app_logs_dir = get_app_logs_dir(create=True)

    server_port_value = os.getenv("SERVER_PORT", "8000")
    try:
        server_port = int(server_port_value)
    except ValueError as exc:
        raise ValueError(f"Invalid SERVER_PORT: {server_port_value}") from exc

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_data_dir=app_data_dir,
        app_logs_dir=app_logs_dir,
        server_host=os.getenv("SERVER_HOST", "0.0.0.0"),
        server_port=server_port,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        kimi_api_key=os.getenv("KIMI_API_KEY"),
    )


def configure_logging() -> Path:
    """Configure backend logging and return the log file path."""
    settings = get_settings()
    log_file_path = settings.app_logs_dir / "backend.log"
    log_level = getattr(logging, settings.log_level, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler_exists = False
    stream_handler_exists = False

    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file_path:
            handler.setLevel(log_level)
            handler.setFormatter(formatter)
            file_handler_exists = True
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.FileHandler
        ):
            handler.setLevel(log_level)
            handler.setFormatter(formatter)
            stream_handler_exists = True

    if not file_handler_exists:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if not stream_handler_exists:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    return log_file_path
