"""Unit tests for diagnostic reporter enhancements."""

import pytest
import uuid
from datetime import datetime
from src.server.modules.diagnostic_reporter import (
    DiagnosticReporter, ErrorAnalyzer
)
from src.server.modules.run_orchestrator import (
    RetryableError, ResourceError, ValidationError, DependencyError
)
from src.server.modules.project_manager import ProjectManager
from src.shared.types import (
    ProjectInputContract, ErrorType, DiagnosticEvent,
    RecoverySuggestion, PerformanceMetrics
)
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import RunRecordEnhanced


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


class TestErrorAnalyzer:
    """Test ErrorAnalyzer functionality."""

    def test_analyze_retryable_error(self):
        """Test analyzing retryable error."""
        error = RetryableError("Network timeout")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "narration_generation"}
        )

        assert analysis is not None
        assert analysis["error_type"] == "RetryableError"
        assert analysis["recovery_type"] == ErrorType.RETRYABLE.value
        assert analysis["stage_name"] == "narration_generation"

    def test_analyze_resource_error(self):
        """Test analyzing resource error."""
        error = ResourceError("Out of memory")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "media_analysis"}
        )

        assert analysis["error_type"] == "ResourceError"
        assert analysis["recovery_type"] == ErrorType.RESOURCE.value

    def test_analyze_validation_error(self):
        """Test analyzing validation error."""
        error = ValidationError("Invalid input")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "input_validation"}
        )

        assert analysis["error_type"] == "ValidationError"
        assert analysis["recovery_type"] == ErrorType.VALIDATION.value

    def test_analyze_dependency_error(self):
        """Test analyzing dependency error."""
        error = DependencyError("Missing upstream artifact")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "narration_generation"}
        )

        assert analysis["error_type"] == "DependencyError"
        assert analysis["recovery_type"] == ErrorType.DEPENDENCY.value

    def test_generate_recovery_suggestions(self):
        """Test generating recovery suggestions."""
        error = RetryableError("Network timeout")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "narration_generation"}
        )

        suggestions = ErrorAnalyzer.generate_recovery_suggestions(analysis)

        assert len(suggestions) > 0
        assert all(isinstance(s, RecoverySuggestion) for s in suggestions)
        assert suggestions[0].error_type == ErrorType.RETRYABLE

    def test_recovery_suggestions_priority(self):
        """Test recovery suggestions have priority."""
        error = ResourceError("Out of memory")
        analysis = ErrorAnalyzer.analyze_error(
            error,
            {"stage_name": "media_analysis"}
        )

        suggestions = ErrorAnalyzer.generate_recovery_suggestions(analysis)

        assert all(1 <= s.priority <= 5 for s in suggestions)


class TestDiagnosticReporter:
    """Test DiagnosticReporter functionality."""

    def test_log_diagnostic(self, test_project):
        """Test logging diagnostic."""
        run_id = str(uuid.uuid4())

        DiagnosticReporter.log_diagnostic(
            test_project,
            run_id,
            "test_issue",
            "error",
            "Test error message"
        )
        # Should not raise exception

    def test_log_fallback(self, test_project):
        """Test logging fallback."""
        run_id = str(uuid.uuid4())

        DiagnosticReporter.log_fallback(
            test_project,
            run_id,
            "metadata_missing",
            "semantic_align",
            {"details": "test"}
        )
        # Should not raise exception

    def test_generate_diagnostic_bundle(self, test_project):
        """Test generating diagnostic bundle."""
        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=test_project,
                run_type="full_pipeline",
                state="completed",
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                test_project, run_record.run_id, run_record
            )

            assert bundle is not None
            assert bundle.run_id == run_record.run_id
            assert bundle.project_id == test_project
            assert bundle.run_summary is not None

        finally:
            session.close()

    def test_export_diagnostic_bundle_json(self, test_project):
        """Test exporting bundle as JSON."""
        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=test_project,
                run_type="full_pipeline",
                state="completed",
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                test_project, run_record.run_id, run_record
            )

            json_export = DiagnosticReporter.export_diagnostic_bundle(bundle, "json")

            assert json_export is not None
            assert isinstance(json_export, str)
            assert "run_id" in json_export

        finally:
            session.close()

    def test_export_diagnostic_bundle_markdown(self, test_project):
        """Test exporting bundle as Markdown."""
        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=test_project,
                run_type="full_pipeline",
                state="completed",
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                test_project, run_record.run_id, run_record
            )

            md_export = DiagnosticReporter.export_diagnostic_bundle(bundle, "markdown")

            assert md_export is not None
            assert isinstance(md_export, str)
            assert "Diagnostic Report" in md_export

        finally:
            session.close()

    def test_export_diagnostic_bundle_html(self, test_project):
        """Test exporting bundle as HTML."""
        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=test_project,
                run_type="full_pipeline",
                state="completed",
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                test_project, run_record.run_id, run_record
            )

            html_export = DiagnosticReporter.export_diagnostic_bundle(bundle, "html")

            assert html_export is not None
            assert isinstance(html_export, str)
            assert "<html>" in html_export

        finally:
            session.close()

    def test_generate_recovery_manifest(self, test_project):
        """Test generating recovery manifest."""
        db = get_or_create_db(test_project)
        session = db.get_session()

        try:
            run_record = RunRecordEnhanced(
                run_id=str(uuid.uuid4()),
                project_id=test_project,
                run_type="full_pipeline",
                state="failed_retryable",
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            session.add(run_record)
            session.commit()

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                test_project, run_record.run_id, run_record
            )

            manifest = DiagnosticReporter.generate_recovery_manifest(bundle)

            assert manifest is not None
            assert "recovery_steps" in manifest
            assert "next_actions" in manifest
            assert manifest["run_id"] == run_record.run_id

        finally:
            session.close()

    def test_get_user_message_completed(self):
        """Test user message for completed run."""
        msg = DiagnosticReporter.get_user_message("completed", 0, 0)
        assert "successfully" in msg.lower()

    def test_get_user_message_completed_with_fallbacks(self):
        """Test user message for completed run with fallbacks."""
        msg = DiagnosticReporter.get_user_message("completed", 0, 2)
        assert "fallback" in msg.lower()

    def test_get_user_message_failed(self):
        """Test user message for failed run."""
        msg = DiagnosticReporter.get_user_message("failed", 3, 0)
        assert "failed" in msg.lower()
        assert "3" in msg

    def test_get_user_message_in_progress(self):
        """Test user message for in-progress run."""
        msg = DiagnosticReporter.get_user_message("running", 0, 0)
        assert "progress" in msg.lower()
