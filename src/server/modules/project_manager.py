"""Project Manager module."""

import shutil
import uuid
from datetime import datetime
from typing import List, Optional

from src.shared.types import ProjectInputContract
from src.server.models.project import ProjectConfig, ProjectMetadata
from src.server.storage.database import Database, get_or_create_db, get_project_dir, get_projects_root_dir
from src.server.storage.schemas import (
    AssetIndexRecord,
    MediaFileRecord,
    ProjectConfigRecord,
    ProjectRecord,
)


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
    def list_projects() -> List[ProjectMetadata]:
        """List all known projects."""
        projects_root = get_projects_root_dir(create=True)
        project_metadata: List[ProjectMetadata] = []

        for project_dir in projects_root.iterdir():
            if not project_dir.is_dir():
                continue

            db_path = project_dir / "project.db"
            if not db_path.exists():
                continue

            db = Database(str(db_path))
            session = db.get_session()

            try:
                project = session.query(ProjectRecord).first()
                if not project:
                    continue

                asset_index = session.query(AssetIndexRecord).filter(
                    AssetIndexRecord.project_id == project.project_id
                ).first()

                project_metadata.append(
                    ProjectMetadata(
                        project_id=project.project_id,
                        project_name=project.project_name,
                        status=project.status,
                        created_at=project.created_at,
                        updated_at=project.updated_at,
                        total_videos=asset_index.total_videos if asset_index else 0,
                        total_photos=asset_index.total_photos if asset_index else 0,
                        total_duration=asset_index.total_duration if asset_index else 0.0,
                    )
                )
            except Exception:
                continue
            finally:
                session.close()
                db.close()

        return sorted(project_metadata, key=lambda item: item.updated_at, reverse=True)

    @staticmethod
    def get_project_input_contract(project_id: str) -> Optional[ProjectInputContract]:
        """Reconstruct the original project input contract from persisted data."""
        metadata = ProjectManager.get_project_metadata(project_id)
        config = ProjectManager.get_project_config(project_id)
        if not metadata or not config:
            return None

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            media_files = [
                record.file_path
                for record in session.query(MediaFileRecord)
                .filter(MediaFileRecord.project_id == project_id)
                .order_by(MediaFileRecord.indexed_at.asc(), MediaFileRecord.file_path.asc())
                .all()
            ]

            return ProjectInputContract(
                project_name=metadata.project_name,
                travel_note=config.travel_note,
                media_files=media_files,
                bgm_asset=config.bgm_asset,
                tts_voice=config.tts_voice,
                metadata_pack=config.metadata_pack,
            )
        finally:
            session.close()

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Delete project workspace and database."""
        project_dir = get_project_dir(project_id, create=False)
        if not project_dir.exists():
            return False

        shutil.rmtree(project_dir, ignore_errors=False)
        return True

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
