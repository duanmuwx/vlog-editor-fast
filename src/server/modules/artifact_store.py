"""Artifact version management and dependency tracking."""

import uuid
from datetime import datetime
from typing import Optional, Dict
from src.shared.types import ArtifactVersion
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import ArtifactVersionRecord


class ArtifactStore:
    """Manages artifact versions and dependencies."""

    @staticmethod
    def create_version(
        artifact_type: str,
        project_id: str,
        upstream_versions: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create new artifact version.

        Args:
            artifact_type: Type of artifact ("timeline", "narration", "audio_mix", "export")
            project_id: Project ID
            upstream_versions: Dict of upstream dependencies

        Returns:
            version_id of created version
        """
        version_id = str(uuid.uuid4())

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            record = ArtifactVersionRecord(
                version_id=version_id,
                artifact_type=artifact_type,
                project_id=project_id,
                upstream_versions=upstream_versions or {},
                status="active",
                created_at=datetime.utcnow()
            )
            session.add(record)
            session.commit()
            return version_id
        finally:
            session.close()

    @staticmethod
    def get_version(version_id: str, project_id: str) -> Optional[ArtifactVersion]:
        """Retrieve artifact version."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            record = session.query(ArtifactVersionRecord).filter_by(
                version_id=version_id
            ).first()

            if not record:
                return None

            return ArtifactVersion(
                version_id=record.version_id,
                artifact_type=record.artifact_type,
                project_id=record.project_id,
                upstream_versions=record.upstream_versions or {},
                status=record.status,
                created_at=record.created_at,
                invalidated_at=record.invalidated_at
            )
        finally:
            session.close()

    @staticmethod
    def invalidate_version(version_id: str, project_id: str) -> None:
        """
        Invalidate version and all downstream versions.

        Args:
            version_id: Version to invalidate
            project_id: Project ID
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Invalidate the version
            record = session.query(ArtifactVersionRecord).filter_by(
                version_id=version_id
            ).first()

            if record:
                record.status = "invalidated"
                record.invalidated_at = datetime.utcnow()
                session.commit()

            # Invalidate all downstream versions that depend on this one
            downstream = session.query(ArtifactVersionRecord).filter(
                ArtifactVersionRecord.project_id == project_id,
                ArtifactVersionRecord.status == "active"
            ).all()

            for downstream_record in downstream:
                if downstream_record.upstream_versions:
                    if version_id in downstream_record.upstream_versions.values():
                        downstream_record.status = "invalidated"
                        downstream_record.invalidated_at = datetime.utcnow()

            session.commit()
        finally:
            session.close()

    @staticmethod
    def get_active_version(
        project_id: str,
        artifact_type: str
    ) -> Optional[ArtifactVersion]:
        """Get active version of artifact type."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            record = session.query(ArtifactVersionRecord).filter(
                ArtifactVersionRecord.project_id == project_id,
                ArtifactVersionRecord.artifact_type == artifact_type,
                ArtifactVersionRecord.status == "active"
            ).order_by(ArtifactVersionRecord.created_at.desc()).first()

            if not record:
                return None

            return ArtifactVersion(
                version_id=record.version_id,
                artifact_type=record.artifact_type,
                project_id=record.project_id,
                upstream_versions=record.upstream_versions or {},
                status=record.status,
                created_at=record.created_at,
                invalidated_at=record.invalidated_at
            )
        finally:
            session.close()

    @staticmethod
    def rollback_version(
        project_id: str,
        artifact_type: str,
        version_id: str
    ) -> None:
        """
        Rollback to previous version.

        Args:
            project_id: Project ID
            artifact_type: Type of artifact
            version_id: Version to rollback to
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Mark current active version as superseded
            current = session.query(ArtifactVersionRecord).filter(
                ArtifactVersionRecord.project_id == project_id,
                ArtifactVersionRecord.artifact_type == artifact_type,
                ArtifactVersionRecord.status == "active"
            ).first()

            if current:
                current.status = "superseded"
                session.commit()

            # Mark target version as active
            target = session.query(ArtifactVersionRecord).filter_by(
                version_id=version_id
            ).first()

            if target:
                target.status = "active"
                session.commit()
        finally:
            session.close()

    @staticmethod
    def mark_superseded(version_id: str, project_id: str) -> None:
        """Mark version as superseded."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            record = session.query(ArtifactVersionRecord).filter_by(
                version_id=version_id
            ).first()

            if record:
                record.status = "superseded"
                session.commit()
        finally:
            session.close()
