"""Project Manager module."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.shared.types import ProjectInputContract
from src.server.models.project import ProjectConfig, ProjectMetadata
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import ProjectRecord, ProjectConfigRecord


class ProjectManager:
    """Manages project creation and configuration."""

    @staticmethod
    def create_project(input_contract: ProjectInputContract) -> str:
        """Create a new project and return project_id."""
        project_id = str(uuid.uuid4())

        # Initialize database
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Create project record
            project = ProjectRecord(
                project_id=project_id,
                project_name=input_contract.project_name,
                status="draft",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(project)

            # Create project config record
            config_id = str(uuid.uuid4())
            config = ProjectConfigRecord(
                config_id=config_id,
                project_id=project_id,
                travel_note=input_contract.travel_note,
                bgm_asset=input_contract.bgm_asset,
                tts_voice=input_contract.tts_voice,
                metadata_pack=input_contract.metadata_pack,
                created_at=datetime.utcnow()
            )
            session.add(config)
            session.commit()

            return project_id
        finally:
            session.close()

    @staticmethod
    def get_project_config(project_id: str) -> Optional[ProjectConfig]:
        """Get project configuration."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            config_record = session.query(ProjectConfigRecord).filter(
                ProjectConfigRecord.project_id == project_id
            ).first()

            if not config_record:
                return None

            return ProjectConfig(
                project_id=project_id,
                travel_note=config_record.travel_note,
                bgm_asset=config_record.bgm_asset,
                tts_voice=config_record.tts_voice,
                metadata_pack=config_record.metadata_pack,
                created_at=config_record.created_at,
                updated_at=datetime.utcnow()
            )
        finally:
            session.close()

    @staticmethod
    def get_project_metadata(project_id: str) -> Optional[ProjectMetadata]:
        """Get project metadata."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            project = session.query(ProjectRecord).filter(
                ProjectRecord.project_id == project_id
            ).first()

            if not project:
                return None

            return ProjectMetadata(
                project_id=project_id,
                project_name=project.project_name,
                status=project.status,
                created_at=project.created_at,
                updated_at=project.updated_at
            )
        finally:
            session.close()

    @staticmethod
    def update_project_status(project_id: str, status: str) -> None:
        """Update project status."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            project = session.query(ProjectRecord).filter(
                ProjectRecord.project_id == project_id
            ).first()

            if project:
                project.status = status
                project.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
