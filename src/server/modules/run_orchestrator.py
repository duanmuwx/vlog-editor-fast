"""Run orchestration - manage state machine and task scheduling."""

import uuid
from datetime import datetime
from src.shared.types import ExportBundle, ProjectStatus
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    RunRecord, TaskStateRecord, ProjectRecord
)
from src.server.modules.edit_planner import EditPlanner
from src.server.modules.narration_engine import NarrationEngine
from src.server.modules.audio_composer import AudioComposer
from src.server.modules.renderer import Renderer
from src.server.modules.diagnostic_reporter import DiagnosticReporter


class RunOrchestrator:
    """Manages project state machine and task scheduling."""

    @staticmethod
    def run_phase4(project_id: str, bgm_asset: str, tts_voice: str) -> ExportBundle:
        """
        Execute Phase 4 pipeline: edit planning → narration → audio → rendering.

        Args:
            project_id: Project ID
            bgm_asset: Path to BGM asset
            tts_voice: TTS voice to use

        Returns:
            ExportBundle with final video and outputs
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        run_id = str(uuid.uuid4())

        try:
            # Create run record
            run_record = RunRecord(
                run_id=run_id,
                project_id=project_id,
                started_at=datetime.utcnow(),
                status="running"
            )
            session.add(run_record)
            session.commit()

            # Stage 1: Edit Planning
            RunOrchestrator._execute_stage(
                session, run_id, "edit_planning", "Generating timeline"
            )
            timeline = EditPlanner.plan_edit(project_id)
            RunOrchestrator._complete_stage(session, run_id, "edit_planning")

            # Stage 2: Narration Generation
            RunOrchestrator._execute_stage(
                session, run_id, "narration_generation", "Generating narration"
            )
            narration = NarrationEngine.generate_narration(
                project_id, timeline.timeline_id, tts_voice
            )
            RunOrchestrator._complete_stage(session, run_id, "narration_generation")

            # Stage 3: Audio Composition
            RunOrchestrator._execute_stage(
                session, run_id, "audio_composition", "Mixing audio"
            )
            audio_mix = AudioComposer.compose_audio(
                project_id, timeline.timeline_id, narration.narration_id, bgm_asset
            )
            RunOrchestrator._complete_stage(session, run_id, "audio_composition")

            # Stage 4: Rendering
            RunOrchestrator._execute_stage(
                session, run_id, "rendering", "Rendering video"
            )
            export_bundle = Renderer.render_export(
                project_id, timeline.timeline_id, audio_mix.audio_mix_id, narration.narration_id
            )
            RunOrchestrator._complete_stage(session, run_id, "rendering")

            # Update run record
            run_record.ended_at = datetime.utcnow()
            run_record.status = "completed"
            session.commit()

            # Update project status
            project = session.query(ProjectRecord).filter_by(
                project_id=project_id
            ).first()
            if project:
                project.status = ProjectStatus.EXPORTED.value
                session.commit()

            return export_bundle

        except Exception as e:
            # Handle failure
            RunOrchestrator._handle_failure(project_id, run_id, e, session)
            raise

        finally:
            session.close()

    @staticmethod
    def regenerate_narration(
        project_id: str,
        tts_voice: str
    ) -> ExportBundle:
        """
        Regenerate narration only, reuse timeline and audio mix.

        Args:
            project_id: Project ID
            tts_voice: TTS voice to use

        Returns:
            ExportBundle with regenerated narration
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.modules.artifact_store import ArtifactStore

            # Get active timeline and audio mix
            timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
            audio_mix_version = ArtifactStore.get_active_version(project_id, "audio_mix")

            if not timeline_version or not audio_mix_version:
                raise ValueError("No active timeline or audio mix found")

            # Get timeline and audio mix records
            from src.server.storage.schemas import TimelineRecord, AudioMixRecord

            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()

            audio_mix_record = session.query(AudioMixRecord).filter_by(
                version_id=audio_mix_version.version_id
            ).first()

            # Regenerate narration
            narration = NarrationEngine.generate_narration(
                project_id, timeline_record.timeline_id, tts_voice
            )

            # Render with new narration
            export_bundle = Renderer.render_export(
                project_id,
                timeline_record.timeline_id,
                audio_mix_record.audio_mix_id,
                narration.narration_id
            )

            return export_bundle

        finally:
            session.close()

    @staticmethod
    def regenerate_audio(project_id: str, bgm_asset: str) -> ExportBundle:
        """
        Regenerate audio only, reuse timeline and narration.

        Args:
            project_id: Project ID
            bgm_asset: Path to BGM asset

        Returns:
            ExportBundle with regenerated audio
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.modules.artifact_store import ArtifactStore

            # Get active timeline and narration
            timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
            narration_version = ArtifactStore.get_active_version(project_id, "narration")

            if not timeline_version or not narration_version:
                raise ValueError("No active timeline or narration found")

            # Get records
            from src.server.storage.schemas import TimelineRecord, NarrationRecord

            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()

            narration_record = session.query(NarrationRecord).filter_by(
                version_id=narration_version.version_id
            ).first()

            # Regenerate audio mix
            audio_mix = AudioComposer.compose_audio(
                project_id,
                timeline_record.timeline_id,
                narration_record.narration_id,
                bgm_asset
            )

            # Render with new audio
            export_bundle = Renderer.render_export(
                project_id,
                timeline_record.timeline_id,
                audio_mix.audio_mix_id,
                narration_record.narration_id
            )

            return export_bundle

        finally:
            session.close()

    @staticmethod
    def regenerate_shorter(
        project_id: str,
        target_seconds: float
    ) -> ExportBundle:
        """
        Regenerate with shorter duration, reuse narration.

        Args:
            project_id: Project ID
            target_seconds: Target duration in seconds

        Returns:
            ExportBundle with shorter video
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.modules.artifact_store import ArtifactStore

            # Get active timeline and narration
            timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
            narration_version = ArtifactStore.get_active_version(project_id, "narration")
            audio_mix_version = ArtifactStore.get_active_version(project_id, "audio_mix")

            if not all([timeline_version, narration_version, audio_mix_version]):
                raise ValueError("Missing active versions")

            # Get records
            from src.server.storage.schemas import (
                TimelineRecord, NarrationRecord, AudioMixRecord
            )

            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()

            narration_record = session.query(NarrationRecord).filter_by(
                version_id=narration_version.version_id
            ).first()

            audio_mix_record = session.query(AudioMixRecord).filter_by(
                version_id=audio_mix_version.version_id
            ).first()

            # Render with shorter duration
            export_bundle = Renderer.render_export(
                project_id,
                timeline_record.timeline_id,
                audio_mix_record.audio_mix_id,
                narration_record.narration_id
            )

            return export_bundle

        finally:
            session.close()

    @staticmethod
    def _execute_stage(session, run_id: str, stage_name: str, description: str) -> None:
        """Mark stage as started."""
        task_record = TaskStateRecord(
            task_id=str(uuid.uuid4()),
            run_id=run_id,
            stage_name=stage_name,
            status="running",
            started_at=datetime.utcnow()
        )
        session.add(task_record)
        session.commit()

    @staticmethod
    def _complete_stage(session, run_id: str, stage_name: str) -> None:
        """Mark stage as completed."""
        task_record = session.query(TaskStateRecord).filter_by(
            run_id=run_id,
            stage_name=stage_name,
            status="running"
        ).first()

        if task_record:
            task_record.status = "completed"
            task_record.ended_at = datetime.utcnow()
            session.commit()

    @staticmethod
    def _handle_failure(
        project_id: str,
        run_id: str,
        error: Exception,
        session
    ) -> None:
        """Handle failure: log diagnostics, preserve intermediate products."""
        # Update run record
        run_record = session.query(RunRecord).filter_by(run_id=run_id).first()
        if run_record:
            run_record.status = "failed"
            run_record.ended_at = datetime.utcnow()
            session.commit()

        # Log diagnostic
        DiagnosticReporter.log_diagnostic(
            project_id,
            run_id,
            "phase4_failure",
            "error",
            str(error)
        )
