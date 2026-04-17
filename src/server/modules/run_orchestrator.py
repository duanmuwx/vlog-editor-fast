"""Run orchestration - manage state machine and task scheduling."""

import uuid
import asyncio
import logging
from datetime import datetime
from typing import Callable, Optional, Dict, List
from src.shared.types import (
    ExportBundle, ProjectStatus, RunType, RunState, TaskStatus,
    ErrorType, TaskStateRecord as TaskStateType, ErrorInfo,
    RecoverySuggestion, PerformanceMetrics, RunRecord as RunRecordType
)
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    RunRecord, TaskStateRecord, ProjectRecord
)
from src.server.modules.edit_planner import EditPlanner
from src.server.modules.narration_engine import NarrationEngine
from src.server.modules.audio_composer import AudioComposer
from src.server.modules.renderer import Renderer
from src.server.modules.diagnostic_reporter import DiagnosticReporter

logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """Error that can be retried."""
    pass


class ResourceError(Exception):
    """Resource-related error."""
    pass


class ValidationError(Exception):
    """Validation error."""
    pass


class DependencyError(Exception):
    """Dependency validation error."""
    pass


class RunOrchestrator:
    """Manages project state machine and task scheduling."""

    @staticmethod
    async def run_with_retry(
        stage_name: str,
        stage_func: Callable,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> TaskStateType:
        """Execute stage with retry logic."""
        for attempt in range(max_retries):
            try:
                result = await stage_func()
                return TaskStateType(
                    task_id=str(uuid.uuid4()),
                    run_id="",
                    stage_name=stage_name,
                    status=TaskStatus.SUCCEEDED,
                    started_at=datetime.utcnow(),
                    ended_at=datetime.utcnow(),
                    attempt=attempt + 1
                )
            except RetryableError as e:
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Stage {stage_name} failed (attempt {attempt + 1}), "
                        f"retrying in {wait_time}s: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return TaskStateType(
                        task_id=str(uuid.uuid4()),
                        run_id="",
                        stage_name=stage_name,
                        status=TaskStatus.FAILED_RETRYABLE,
                        started_at=datetime.utcnow(),
                        ended_at=datetime.utcnow(),
                        attempt=attempt + 1,
                        error_message=str(e),
                        error_type=ErrorType.RETRYABLE
                    )
            except Exception as e:
                return TaskStateType(
                    task_id=str(uuid.uuid4()),
                    run_id="",
                    stage_name=stage_name,
                    status=TaskStatus.FAILED_MANUAL,
                    started_at=datetime.utcnow(),
                    ended_at=datetime.utcnow(),
                    attempt=attempt + 1,
                    error_message=str(e),
                    error_type=ErrorType.MANUAL
                )

    @staticmethod
    def run_phase4(project_id: str, bgm_asset: str, tts_voice: str) -> ExportBundle:
        """Execute Phase 4 pipeline: edit planning → narration → audio → rendering."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        run_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        stage_durations = {}

        try:
            run_record = RunRecord(
                run_id=run_id,
                project_id=project_id,
                started_at=start_time,
                status="running",
                run_type=RunType.FULL_PIPELINE.value
            )
            session.add(run_record)
            session.commit()

            # Stage 1: Edit Planning
            stage_start = datetime.utcnow()
            RunOrchestrator._execute_stage(
                session, run_id, "edit_planning", "Generating timeline"
            )
            timeline = EditPlanner.plan_edit(project_id)
            RunOrchestrator._complete_stage(session, run_id, "edit_planning")
            stage_durations["edit_planning"] = (datetime.utcnow() - stage_start).total_seconds()

            # Stage 2: Narration Generation
            stage_start = datetime.utcnow()
            RunOrchestrator._execute_stage(
                session, run_id, "narration_generation", "Generating narration"
            )
            narration = NarrationEngine.generate_narration(
                project_id, timeline.timeline_id, tts_voice
            )
            RunOrchestrator._complete_stage(session, run_id, "narration_generation")
            stage_durations["narration_generation"] = (datetime.utcnow() - stage_start).total_seconds()

            # Stage 3: Audio Composition
            stage_start = datetime.utcnow()
            RunOrchestrator._execute_stage(
                session, run_id, "audio_composition", "Mixing audio"
            )
            audio_mix = AudioComposer.compose_audio(
                project_id, timeline.timeline_id, narration.narration_id, bgm_asset
            )
            RunOrchestrator._complete_stage(session, run_id, "audio_composition")
            stage_durations["audio_composition"] = (datetime.utcnow() - stage_start).total_seconds()

            # Stage 4: Rendering
            stage_start = datetime.utcnow()
            RunOrchestrator._execute_stage(
                session, run_id, "rendering", "Rendering video"
            )
            export_bundle = Renderer.render_export(
                project_id, timeline.timeline_id, audio_mix.audio_mix_id, narration.narration_id
            )
            RunOrchestrator._complete_stage(session, run_id, "rendering")
            stage_durations["rendering"] = (datetime.utcnow() - stage_start).total_seconds()

            run_record.ended_at = datetime.utcnow()
            run_record.status = "completed"
            run_record.performance_metrics = {
                "total_duration_seconds": (run_record.ended_at - start_time).total_seconds(),
                "stage_durations": stage_durations
            }
            session.commit()

            project = session.query(ProjectRecord).filter_by(
                project_id=project_id
            ).first()
            if project:
                project.status = ProjectStatus.EXPORTED.value
                session.commit()

            logger.info(f"Phase 4 completed for project {project_id}")
            return export_bundle

        except Exception as e:
            RunOrchestrator._handle_failure(project_id, run_id, e, session)
            raise

        finally:
            session.close()

    @staticmethod
    def regenerate_narration(project_id: str, tts_voice: str) -> ExportBundle:
        """Regenerate narration only, reuse timeline and audio mix."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.modules.artifact_store import ArtifactStore

            timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
            audio_mix_version = ArtifactStore.get_active_version(project_id, "audio_mix")

            if not timeline_version or not audio_mix_version:
                raise ValueError("No active timeline or audio mix found")

            from src.server.storage.schemas import TimelineRecord, AudioMixRecord

            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()

            audio_mix_record = session.query(AudioMixRecord).filter_by(
                version_id=audio_mix_version.version_id
            ).first()

            narration = NarrationEngine.generate_narration(
                project_id, timeline_record.timeline_id, tts_voice
            )

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
        """Regenerate audio only, reuse timeline and narration."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.modules.artifact_store import ArtifactStore

            timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
            narration_version = ArtifactStore.get_active_version(project_id, "narration")

            if not timeline_version or not narration_version:
                raise ValueError("No active timeline or narration found")

            from src.server.storage.schemas import TimelineRecord, NarrationRecord

            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()

            narration_record = session.query(NarrationRecord).filter_by(
                version_id=narration_version.version_id
            ).first()

            audio_mix = AudioComposer.compose_audio(
                project_id,
                timeline_record.timeline_id,
                narration_record.narration_id,
                bgm_asset
            )

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
    def regenerate_shorter(project_id: str, target_seconds: float) -> ExportBundle:
        """Regenerate with shorter duration, reuse narration."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.modules.artifact_store import ArtifactStore

            timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
            narration_version = ArtifactStore.get_active_version(project_id, "narration")
            audio_mix_version = ArtifactStore.get_active_version(project_id, "audio_mix")

            if not all([timeline_version, narration_version, audio_mix_version]):
                raise ValueError("Missing active versions")

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
        run_record = session.query(RunRecord).filter_by(run_id=run_id).first()
        if run_record:
            run_record.status = "failed"
            run_record.ended_at = datetime.utcnow()
            session.commit()

        DiagnosticReporter.log_diagnostic(
            project_id,
            run_id,
            "phase4_failure",
            "error",
            str(error)
        )
