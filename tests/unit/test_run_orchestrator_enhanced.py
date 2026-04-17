"""Unit tests for run orchestrator enhancements."""

import pytest
import asyncio
from datetime import datetime
from src.server.modules.run_orchestrator import (
    RunOrchestrator, RetryableError, ResourceError,
    ValidationError, DependencyError
)
from src.server.modules.project_manager import ProjectManager
from src.shared.types import ProjectInputContract, TaskStatus, ErrorType


@pytest.fixture
def test_project():
    """Create test project."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="Test narrative",
        media_files=[],
        bgm_asset="test.mp3",
        tts_voice="default"
    )
    return ProjectManager.create_project(input_contract)


class TestRunWithRetry:
    """Test run with retry functionality."""

    @pytest.mark.asyncio
    async def test_run_with_retry_success(self):
        """Test successful run with retry."""
        call_count = 0

        async def test_stage():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await RunOrchestrator.run_with_retry(
            "test_stage",
            test_stage,
            max_retries=3
        )

        assert result.status == TaskStatus.SUCCEEDED
        assert result.attempt == 1
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_run_with_retry_retryable_error(self):
        """Test run with retryable error."""
        call_count = 0

        async def test_stage():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RetryableError("Temporary failure")
            return "success"

        result = await RunOrchestrator.run_with_retry(
            "test_stage",
            test_stage,
            max_retries=3,
            backoff_factor=0.1
        )

        assert result.status == TaskStatus.SUCCEEDED
        assert result.attempt == 3
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_run_with_retry_max_retries_exceeded(self):
        """Test run with max retries exceeded."""
        call_count = 0

        async def test_stage():
            nonlocal call_count
            call_count += 1
            raise RetryableError("Persistent failure")

        result = await RunOrchestrator.run_with_retry(
            "test_stage",
            test_stage,
            max_retries=3,
            backoff_factor=0.1
        )

        assert result.status == TaskStatus.FAILED_RETRYABLE
        assert result.attempt == 3
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_run_with_retry_manual_error(self):
        """Test run with manual error."""
        async def test_stage():
            raise ValueError("Manual error")

        result = await RunOrchestrator.run_with_retry(
            "test_stage",
            test_stage,
            max_retries=3
        )

        assert result.status == TaskStatus.FAILED_MANUAL
        assert result.error_type == ErrorType.MANUAL


class TestErrorTypes:
    """Test error type definitions."""

    def test_retryable_error(self):
        """Test RetryableError."""
        error = RetryableError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_resource_error(self):
        """Test ResourceError."""
        error = ResourceError("Out of memory")
        assert isinstance(error, Exception)
        assert str(error) == "Out of memory"

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input")
        assert isinstance(error, Exception)
        assert str(error) == "Invalid input"

    def test_dependency_error(self):
        """Test DependencyError."""
        error = DependencyError("Missing dependency")
        assert isinstance(error, Exception)
        assert str(error) == "Missing dependency"


class TestRunPhase4:
    """Test Phase 4 run execution."""

    def test_run_phase4_basic(self, test_project):
        """Test basic Phase 4 run."""
        # This would require full Phase 1-3 setup
        # Placeholder for integration test
        pass


class TestRegenerationMethods:
    """Test regeneration methods."""

    def test_regenerate_narration_basic(self, test_project):
        """Test narration regeneration."""
        # This would require full Phase 4 setup
        # Placeholder for integration test
        pass

    def test_regenerate_audio_basic(self, test_project):
        """Test audio regeneration."""
        # This would require full Phase 4 setup
        # Placeholder for integration test
        pass

    def test_regenerate_shorter_basic(self, test_project):
        """Test shorter duration regeneration."""
        # This would require full Phase 4 setup
        # Placeholder for integration test
        pass


class TestStageExecution:
    """Test stage execution helpers."""

    def test_execute_stage(self, test_project):
        """Test executing stage."""
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecord

        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecord(
                run_id="test_run_id",
                project_id=test_project,
                started_at=datetime.utcnow(),
                status="running"
            )
            session.add(run_record)
            session.commit()

            RunOrchestrator._execute_stage(
                session, "test_run_id", "test_stage", "Testing stage"
            )

            # Verify task was created
            from src.server.storage.schemas import TaskStateRecord
            task = session.query(TaskStateRecord).filter_by(
                run_id="test_run_id",
                stage_name="test_stage"
            ).first()

            assert task is not None
            assert task.status == "running"

        finally:
            session.close()

    def test_complete_stage(self, test_project):
        """Test completing stage."""
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecord, TaskStateRecord

        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecord(
                run_id="test_run_id",
                project_id=test_project,
                started_at=datetime.utcnow(),
                status="running"
            )
            session.add(run_record)
            session.commit()

            RunOrchestrator._execute_stage(
                session, "test_run_id", "test_stage", "Testing stage"
            )

            RunOrchestrator._complete_stage(session, "test_run_id", "test_stage")

            task = session.query(TaskStateRecord).filter_by(
                run_id="test_run_id",
                stage_name="test_stage"
            ).first()

            assert task is not None
            assert task.status == "completed"
            assert task.ended_at is not None

        finally:
            session.close()

    def test_handle_failure(self, test_project):
        """Test failure handling."""
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecord

        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecord(
                run_id="test_run_id",
                project_id=test_project,
                started_at=datetime.utcnow(),
                status="running"
            )
            session.add(run_record)
            session.commit()

            error = Exception("Test error")
            RunOrchestrator._handle_failure(
                test_project, "test_run_id", error, session
            )

            # Verify run was marked as failed
            run = session.query(RunRecord).filter_by(
                run_id="test_run_id"
            ).first()

            assert run is not None
            assert run.status == "failed"
            assert run.ended_at is not None

        finally:
            session.close()
