"""Database initialization and connection management."""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
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


def get_project_db_path(project_id: str) -> str:
    """Get project database path."""
    base_dir = Path.home() / ".vlog-editor" / "projects" / project_id
    base_dir.mkdir(parents=True, exist_ok=True)
    return str(base_dir / "project.db")


def get_or_create_db(project_id: str) -> Database:
    """Get or create project database."""
    db_path = get_project_db_path(project_id)
    db = Database(db_path)
    db.init_db()
    return db
