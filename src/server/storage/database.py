"""Database initialization and connection management."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .schemas import Base


class Database:
    """Database manager."""

    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Initialize database tables."""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def close(self):
        """Close database connection."""
        self.engine.dispose()


def get_app_data_dir(create: bool = True) -> Path:
    """Get the application data directory."""
    base_dir = Path(os.getenv("APP_DATA_DIR", "~/.vlog-editor")).expanduser()
    if create:
        base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_projects_root_dir(create: bool = True) -> Path:
    """Get the root directory for all projects."""
    base_dir = get_app_data_dir(create=create) / "projects"
    if create:
        base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_app_logs_dir(create: bool = True) -> Path:
    """Get the application log directory."""
    logs_dir = get_app_data_dir(create=create) / "logs"
    if create:
        logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_project_dir(project_id: str, create: bool = True) -> Path:
    """Get the directory for a specific project."""
    base_dir = get_projects_root_dir(create=create) / project_id
    if create:
        base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_project_db_path(project_id: str) -> str:
    """Get project database path."""
    return str(get_project_dir(project_id) / "project.db")


def get_project_subdir(project_id: str, subdir: str, create: bool = True) -> Path:
    """Get a subdirectory inside a project workspace."""
    target_dir = get_project_dir(project_id, create=create) / subdir
    if create:
        target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def get_or_create_db(project_id: str) -> Database:
    """Get or create project database."""
    db_path = get_project_db_path(project_id)
    db = Database(db_path)
    db.init_db()
    return db
