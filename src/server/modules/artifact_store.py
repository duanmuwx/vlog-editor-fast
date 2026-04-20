"""Artifact version management and dependency tracking."""

import uuid
from datetime import datetime
from typing import Optional, Dict, List
from src.shared.types import ArtifactVersion, VersionHistory, ArtifactDependency
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import ArtifactVersionRecord


class DependencyGraph:
    """Manages artifact dependencies."""

    @staticmethod
    def add_dependency(
        project_id: str,
        downstream_artifact_id: str,
        upstream_artifact_id: str,
        upstream_artifact_type: str
    ) -> None:
        """Record dependency between artifacts."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.storage.schemas import ArtifactDependencyRecord

            record = ArtifactDependencyRecord(
                dependency_id=str(uuid.uuid4()),
                project_id=project_id,
                downstream_artifact_id=downstream_artifact_id,
                upstream_artifact_id=upstream_artifact_id,
                upstream_artifact_type=upstream_artifact_type,
                created_at=datetime.utcnow()
            )
            session.add(record)
            session.commit()
        finally:
            session.close()

    @staticmethod
    def invalidate_downstream(project_id: str, artifact_id: str) -> List[str]:
        """Invalidate all downstream artifacts."""
        db = get_or_create_db(project_id)
        session = db.get_session()
        invalidated = []

        try:
            from src.server.storage.schemas import ArtifactDependencyRecord

            # Find all downstream artifacts
            dependencies = session.query(ArtifactDependencyRecord).filter(
                ArtifactDependencyRecord.project_id == project_id,
                ArtifactDependencyRecord.upstream_artifact_id == artifact_id
            ).all()

            for dep in dependencies:
                # Invalidate downstream artifact
                downstream_record = session.query(ArtifactVersionRecord).filter_by(
                    version_id=dep.downstream_artifact_id
                ).first()

                if downstream_record and downstream_record.status == "active":
                    downstream_record.status = "invalidated"
                    downstream_record.invalidated_at = datetime.utcnow()
                    invalidated.append(dep.downstream_artifact_id)

                    # Recursively invalidate further downstream
                    invalidated.extend(
                        DependencyGraph.invalidate_downstream(
                            project_id, dep.downstream_artifact_id
                        )
                    )

            session.commit()
            return invalidated
        finally:
            session.close()

    @staticmethod
    def get_affected_stages(project_id: str, artifact_id: str) -> List[str]:
        """Get stages affected by artifact change."""
        db = get_or_create_db(project_id)
        session = db.get_session()
        stages = []

        try:
            from src.server.storage.schemas import ArtifactDependencyRecord

            dependencies = session.query(ArtifactDependencyRecord).filter(
                ArtifactDependencyRecord.project_id == project_id,
                ArtifactDependencyRecord.upstream_artifact_id == artifact_id
            ).all()

            for dep in dependencies:
                # Map artifact type to stage
                artifact_type_to_stage = {
                    "timeline": "edit_planning",
                    "narration": "narration_generation",
                    "audio_mix": "audio_composition",
                    "export": "rendering"
                }
                stage = artifact_type_to_stage.get(dep.upstream_artifact_type)
                if stage and stage not in stages:
                    stages.append(stage)

            return stages
        finally:
            session.close()

    @staticmethod
    def validate_upstream(project_id: str, artifact_id: str) -> bool:
        """Validate upstream artifacts are valid."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            record = session.query(ArtifactVersionRecord).filter_by(
                version_id=artifact_id
            ).first()

            if not record or record.status == "invalidated":
                return False

            # Check upstream versions
            if record.upstream_versions:
                for upstream_id in record.upstream_versions.values():
                    upstream_record = session.query(ArtifactVersionRecord).filter_by(
                        version_id=upstream_id
                    ).first()
                    if not upstream_record or upstream_record.status == "invalidated":
                        return False

            return True
        finally:
            session.close()


class VersionReuse:
    """Manages version reuse to avoid redundant computation."""

    @staticmethod
    def can_reuse_version(
        project_id: str,
        artifact_type: str,
        upstream_versions: Dict[str, str]
    ) -> Optional[str]:
        """Check if existing version can be reused."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Find versions with same upstream dependencies
            candidates = session.query(ArtifactVersionRecord).filter(
                ArtifactVersionRecord.project_id == project_id,
                ArtifactVersionRecord.artifact_type == artifact_type,
                ArtifactVersionRecord.status.in_(["active", "superseded"])
            ).all()

            for candidate in candidates:
                if candidate.upstream_versions == upstream_versions:
                    return candidate.version_id

            return None
        finally:
            session.close()

    @staticmethod
    def mark_reused(version_id: str, project_id: str, reused_from: str) -> None:
        """Mark version as reused from another."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            record = session.query(ArtifactVersionRecord).filter_by(
                version_id=version_id
            ).first()

            if record:
                record.reused_from = reused_from
                session.commit()
        finally:
            session.close()


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
            # Mark previous active version as superseded
            previous_active = session.query(ArtifactVersionRecord).filter(
                ArtifactVersionRecord.project_id == project_id,
                ArtifactVersionRecord.artifact_type == artifact_type,
                ArtifactVersionRecord.status == "active"
            ).first()

            if previous_active:
                previous_active.status = "superseded"

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

    @staticmethod
    def get_version_history(
        project_id: str,
        artifact_type: str
    ) -> VersionHistory:
        """Get complete version history for artifact type."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            records = session.query(ArtifactVersionRecord).filter(
                ArtifactVersionRecord.project_id == project_id,
                ArtifactVersionRecord.artifact_type == artifact_type
            ).order_by(ArtifactVersionRecord.created_at.desc()).all()

            versions = [
                ArtifactVersion(
                    version_id=r.version_id,
                    artifact_type=r.artifact_type,
                    project_id=r.project_id,
                    upstream_versions=r.upstream_versions or {},
                    status=r.status,
                    created_at=r.created_at,
                    invalidated_at=r.invalidated_at
                )
                for r in records
            ]

            active_version_id = None
            for v in versions:
                if v.status == "active":
                    active_version_id = v.version_id
                    break

            return VersionHistory(
                artifact_type=artifact_type,
                project_id=project_id,
                versions=versions,
                active_version_id=active_version_id
            )
        finally:
            session.close()

    @staticmethod
    def switch_to_version(
        project_id: str,
        artifact_type: str,
        version_id: str
    ) -> ArtifactVersion:
        """Switch to specified version."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Mark current active as superseded
            current = session.query(ArtifactVersionRecord).filter(
                ArtifactVersionRecord.project_id == project_id,
                ArtifactVersionRecord.artifact_type == artifact_type,
                ArtifactVersionRecord.status == "active"
            ).first()

            if current:
                current.status = "superseded"

            # Mark target as active
            target = session.query(ArtifactVersionRecord).filter_by(
                version_id=version_id
            ).first()

            if not target:
                raise ValueError(f"Version {version_id} not found")

            target.status = "active"
            session.commit()

            return ArtifactVersion(
                version_id=target.version_id,
                artifact_type=target.artifact_type,
                project_id=target.project_id,
                upstream_versions=target.upstream_versions or {},
                status=target.status,
                created_at=target.created_at,
                invalidated_at=target.invalidated_at
            )
        finally:
            session.close()

    @staticmethod
    def get_version_diff(
        project_id: str,
        v1_id: str,
        v2_id: str
    ) -> Dict:
        """Compare two versions."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            v1 = session.query(ArtifactVersionRecord).filter_by(
                version_id=v1_id
            ).first()
            v2 = session.query(ArtifactVersionRecord).filter_by(
                version_id=v2_id
            ).first()

            if not v1 or not v2:
                raise ValueError("Version not found")

            return {
                "v1_id": v1_id,
                "v2_id": v2_id,
                "v1_created_at": v1.created_at,
                "v2_created_at": v2.created_at,
                "v1_status": v1.status,
                "v2_status": v2.status,
                "upstream_changes": {
                    "added": set(v2.upstream_versions.keys()) - set(v1.upstream_versions.keys()),
                    "removed": set(v1.upstream_versions.keys()) - set(v2.upstream_versions.keys()),
                    "modified": [
                        k for k in v1.upstream_versions.keys()
                        if k in v2.upstream_versions and v1.upstream_versions[k] != v2.upstream_versions[k]
                    ]
                }
            }
        finally:
            session.close()
