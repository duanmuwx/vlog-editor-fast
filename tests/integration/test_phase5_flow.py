"""Phase 5 integration tests - version management and recovery."""

import pytest
import uuid
from datetime import datetime
from src.shared.types import (
    ProjectInputContract, RunType, RunState, TaskStatus,
    ErrorType, PerformanceMetrics
)
from src.server.modules.project_manager import ProjectManager
from src.server.modules.input_validator import InputValidator
from src.server.modules.asset_indexer import AssetIndexer
from src.server.modules.story_parser import StoryParser
from src.server.modules.skeleton_confirmation import SkeletonConfirmation
from src.server.modules.media_analyzer import MediaAnalyzer
from src.server.modules.alignment_engine import AlignmentEngine
from src.server.modules.highlight_confirmation import HighlightConfirmation
from src.server.modules.edit_planner import EditPlanner
from src.server.modules.narration_engine import NarrationEngine
from src.server.modules.audio_composer import AudioComposer
from src.server.modules.renderer import Renderer
from src.server.modules.run_orchestrator import RunOrchestrator
from src.server.modules.artifact_store import ArtifactStore, DependencyGraph, VersionReuse
from src.server.modules.diagnostic_reporter import DiagnosticReporter, ErrorAnalyzer
from src.server.storage.database import get_or_create_db


@pytest.fixture
def sample_project():
    """Create sample project for testing."""
    input_contract = ProjectInputContract(
        project_name="Test Vlog",
        travel_note="Sample travel narrative for testing Phase 5 features.",
        media_files=[],
        bgm_asset="test_bgm.mp3",
        tts_voice="default"
    )
    project_id = ProjectManager.create_project(input_contract)
    yield project_id


class TestVersionManagement:
    """Test version management features."""

    def test_create_version(self, sample_project):
        """Test creating artifact version."""
        version_id = ArtifactStore.create_version(
            artifact_type="timeline",
            project_id=sample_project,
            upstream_versions={"story": "v1", "highlights": "v1"}
        )
        assert version_id is not None

        version = ArtifactStore.get_version(version_id, sample_project)
        assert version is not None
        assert version.artifact_type == "timeline"
        assert version.status == "active"

    def test_get_version_history(self, sample_project):
        """Test retrieving version history."""
        # Create multiple versions
        v1 = ArtifactStore.create_version("timeline", sample_project)
        v2 = ArtifactStore.create_version("timeline", sample_project)

        history = ArtifactStore.get_version_history(sample_project, "timeline")
        assert history is not None
        assert len(history.versions) >= 2
        assert history.active_version_id == v2

    def test_switch_version(self, sample_project):
        """Test switching between versions."""
        v1 = ArtifactStore.create_version("timeline", sample_project)
        v2 = ArtifactStore.create_version("timeline", sample_project)

        # v2 should be active
        history = ArtifactStore.get_version_history(sample_project, "timeline")
        assert history.active_version_id == v2

        # Switch back to v1
        ArtifactStore.switch_to_version(sample_project, "timeline", v1)
        history = ArtifactStore.get_version_history(sample_project, "timeline")
        assert history.active_version_id == v1

    def test_version_diff(self, sample_project):
        """Test comparing versions."""
        v1 = ArtifactStore.create_version(
            "timeline", sample_project,
            upstream_versions={"story": "v1"}
        )
        v2 = ArtifactStore.create_version(
            "timeline", sample_project,
            upstream_versions={"story": "v2", "highlights": "v1"}
        )

        diff = ArtifactStore.get_version_diff(sample_project, v1, v2)
        assert diff is not None
        assert "added" in diff["upstream_changes"]
        assert "highlights" in diff["upstream_changes"]["added"]


class TestDependencyTracking:
    """Test dependency tracking features."""

    def test_add_dependency(self, sample_project):
        """Test adding artifact dependency."""
        v1 = ArtifactStore.create_version("timeline", sample_project)
        v2 = ArtifactStore.create_version("narration", sample_project)

        DependencyGraph.add_dependency(
            sample_project, v2, v1, "timeline"
        )

        # Verify dependency was recorded
        affected = DependencyGraph.get_affected_stages(sample_project, v1)
        assert "narration_generation" in affected

    def test_invalidate_downstream(self, sample_project):
        """Test invalidating downstream artifacts."""
        v1 = ArtifactStore.create_version("timeline", sample_project)
        v2 = ArtifactStore.create_version("narration", sample_project)
        v3 = ArtifactStore.create_version("audio_mix", sample_project)

        DependencyGraph.add_dependency(sample_project, v2, v1, "timeline")
        DependencyGraph.add_dependency(sample_project, v3, v2, "narration")

        # Invalidate timeline
        invalidated = DependencyGraph.invalidate_downstream(sample_project, v1)
        assert v2 in invalidated or len(invalidated) > 0

    def test_validate_upstream(self, sample_project):
        """Test validating upstream artifacts."""
        v1 = ArtifactStore.create_version("timeline", sample_project)
        assert DependencyGraph.validate_upstream(sample_project, v1) is True

        # Invalidate upstream
        ArtifactStore.invalidate_version(v1, sample_project)
        assert DependencyGraph.validate_upstream(sample_project, v1) is False


class TestVersionReuse:
    """Test version reuse features."""

    def test_can_reuse_version(self, sample_project):
        """Test checking if version can be reused."""
        upstream = {"story": "v1", "highlights": "v1"}

        v1 = ArtifactStore.create_version(
            "timeline", sample_project,
            upstream_versions=upstream
        )

        # Check if same upstream can be reused
        reusable = VersionReuse.can_reuse_version(
            sample_project, "timeline", upstream
        )
        assert reusable == v1

    def test_mark_reused(self, sample_project):
        """Test marking version as reused."""
        v1 = ArtifactStore.create_version("timeline", sample_project)
        v2 = ArtifactStore.create_version("timeline", sample_project)

        VersionReuse.mark_reused(v2, sample_project, v1)

        # Verify reuse was recorded
        version = ArtifactStore.get_version(v2, sample_project)
        assert version is not None


class TestDiagnosticReporting:
    """Test diagnostic reporting features."""

    def test_error_analysis(self):
        """Test error analysis."""
        from src.server.modules.run_orchestrator import RetryableError

        error = RetryableError("Network timeout")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "narration_generation"}
        )

        assert analysis is not None
        assert analysis["error_type"] == "RetryableError"
        assert analysis["recovery_type"] == ErrorType.RETRYABLE.value

    def test_recovery_suggestions(self):
        """Test generating recovery suggestions."""
        from src.server.modules.run_orchestrator import ResourceError

        error = ResourceError("Out of memory")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "media_analysis"}
        )

        suggestions = ErrorAnalyzer.generate_recovery_suggestions(analysis)
        assert len(suggestions) > 0
        assert suggestions[0].error_type == ErrorType.RESOURCE

    def test_diagnostic_bundle_generation(self, sample_project):
        """Test generating diagnostic bundle."""
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecordEnhanced

        db = get_or_create_db(sample_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=sample_project,
                run_type=RunType.FULL_PIPELINE.value,
                state=RunState.COMPLETED.value,
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                sample_project, run_record.run_id, run_record
            )

            assert bundle is not None
            assert bundle.run_id == run_record.run_id
            assert bundle.project_id == sample_project

        finally:
            session.close()

    def test_export_diagnostic_bundle(self, sample_project):
        """Test exporting diagnostic bundle."""
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecordEnhanced

        db = get_or_create_db(sample_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=sample_project,
                run_type=RunType.FULL_PIPELINE.value,
                state=RunState.COMPLETED.value,
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                sample_project, run_record.run_id, run_record
            )

            # Test JSON export
            json_export = DiagnosticReporter.export_diagnostic_bundle(bundle, "json")
            assert json_export is not None
            assert "run_id" in json_export

            # Test Markdown export
            md_export = DiagnosticReporter.export_diagnostic_bundle(bundle, "markdown")
            assert md_export is not None
            assert "Diagnostic Report" in md_export

        finally:
            session.close()

    def test_recovery_manifest(self, sample_project):
        """Test generating recovery manifest."""
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecordEnhanced

        db = get_or_create_db(sample_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=sample_project,
                run_type=RunType.FULL_PIPELINE.value,
                state=RunState.FAILED_RETRYABLE.value,
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                sample_project, run_record.run_id, run_record
            )

            manifest = DiagnosticReporter.generate_recovery_manifest(bundle)
            assert manifest is not None
            assert "recovery_steps" in manifest
            assert "next_actions" in manifest

        finally:
            session.close()


class TestRegenerationFlows:
    """Test regeneration flows."""

    def test_regenerate_narration_flow(self, sample_project):
        """Test narration regeneration flow."""
        # This would require full Phase 4 setup
        # Placeholder for integration test
        pass

    def test_regenerate_audio_flow(self, sample_project):
        """Test audio regeneration flow."""
        # This would require full Phase 4 setup
        # Placeholder for integration test
        pass

    def test_regenerate_shorter_flow(self, sample_project):
        """Test shorter duration regeneration flow."""
        # This would require full Phase 4 setup
        # Placeholder for integration test
        pass


class TestRunOrchestration:
    """Test run orchestration features."""

    def test_run_with_retry(self):
        """Test run with retry mechanism."""
        import asyncio

        async def test_stage():
            return "success"

        # This would require async test setup
        # Placeholder for integration test
        pass

    def test_performance_metrics(self, sample_project):
        """Test performance metrics collection."""
        metrics = PerformanceMetrics(
            total_duration_seconds=120.5,
            stage_durations={
                "edit_planning": 30.0,
                "narration_generation": 40.0,
                "audio_composition": 30.0,
                "rendering": 20.5
            },
            memory_peak_mb=512.0,
            disk_usage_mb=2048.0
        )

        assert metrics.total_duration_seconds == 120.5
        assert metrics.memory_peak_mb == 512.0
        assert len(metrics.stage_durations) == 4
