"""Diagnostic reporting - aggregate diagnostics and fallback events."""

import uuid
from datetime import datetime
from typing import List, Dict, Optional
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    DiagnosticRecord, FallbackEventRecord, RunRecord
)


class DiagnosticReporter:
    """Aggregates diagnostics and fallback events."""

    @staticmethod
    def log_diagnostic(
        project_id: str,
        run_id: str,
        issue_type: str,
        severity: str,
        message: str
    ) -> None:
        """
        Log diagnostic event.

        Args:
            project_id: Project ID
            run_id: Run ID
            issue_type: Type of issue
            severity: Severity level ("info", "warning", "error")
            message: Diagnostic message
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            diagnostic_record = DiagnosticRecord(
                diagnostic_id=str(uuid.uuid4()),
                project_id=project_id,
                run_id=run_id,
                issue_type=issue_type,
                severity=severity,
                message=message,
                created_at=datetime.utcnow()
            )
            session.add(diagnostic_record)
            session.commit()
        finally:
            session.close()

    @staticmethod
    def log_fallback(
        project_id: str,
        run_id: str,
        reason: str,
        action: str,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log fallback event.

        Args:
            project_id: Project ID
            run_id: Run ID
            reason: Reason for fallback (e.g., "metadata_missing", "insufficient_assets")
            action: Action taken (e.g., "semantic_align", "alternative_render_unit")
            details: Additional details as dict
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            fallback_record = FallbackEventRecord(
                event_id=str(uuid.uuid4()),
                project_id=project_id,
                run_id=run_id,
                reason=reason,
                action=action,
                details=details or {},
                created_at=datetime.utcnow()
            )
            session.add(fallback_record)
            session.commit()
        finally:
            session.close()

    @staticmethod
    def report_diagnostics(project_id: str, run_id: str) -> Dict:
        """
        Aggregate diagnostics from all modules.

        Args:
            project_id: Project ID
            run_id: Run ID

        Returns:
            DiagnosticBundle with all diagnostics and fallback events
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Get run record
            run_record = session.query(RunRecord).filter_by(run_id=run_id).first()

            if not run_record:
                return {"error": "Run not found"}

            # Get diagnostics
            diagnostics = session.query(DiagnosticRecord).filter_by(
                project_id=project_id,
                run_id=run_id
            ).order_by(DiagnosticRecord.created_at).all()

            # Get fallback events
            fallbacks = session.query(FallbackEventRecord).filter_by(
                project_id=project_id,
                run_id=run_id
            ).order_by(FallbackEventRecord.created_at).all()

            # Aggregate by severity
            diagnostics_by_severity = {
                "info": [],
                "warning": [],
                "error": []
            }

            for diagnostic in diagnostics:
                diagnostics_by_severity[diagnostic.severity].append({
                    "issue_type": diagnostic.issue_type,
                    "message": diagnostic.message,
                    "created_at": diagnostic.created_at.isoformat()
                })

            # Aggregate fallback reasons and actions
            fallback_summary = {}
            for fallback in fallbacks:
                key = f"{fallback.reason}:{fallback.action}"
                if key not in fallback_summary:
                    fallback_summary[key] = 0
                fallback_summary[key] += 1

            # Generate summary
            summary = DiagnosticReporter.generate_summary(
                diagnostics, fallbacks, run_record
            )

            return {
                "run_id": run_id,
                "project_id": project_id,
                "status": run_record.status,
                "started_at": run_record.started_at.isoformat(),
                "ended_at": run_record.ended_at.isoformat() if run_record.ended_at else None,
                "diagnostics_by_severity": diagnostics_by_severity,
                "fallback_summary": fallback_summary,
                "total_diagnostics": len(diagnostics),
                "total_fallbacks": len(fallbacks),
                "summary": summary
            }

        finally:
            session.close()

    @staticmethod
    def generate_summary(
        diagnostics: List,
        fallbacks: List,
        run_record
    ) -> str:
        """Generate human-readable run summary."""
        lines = []

        # Status
        lines.append(f"Run Status: {run_record.status.upper()}")

        # Duration
        if run_record.ended_at:
            duration = (run_record.ended_at - run_record.started_at).total_seconds()
            lines.append(f"Duration: {duration:.1f} seconds")

        # Diagnostics summary
        error_count = sum(1 for d in diagnostics if d.severity == "error")
        warning_count = sum(1 for d in diagnostics if d.severity == "warning")

        if error_count > 0:
            lines.append(f"Errors: {error_count}")
        if warning_count > 0:
            lines.append(f"Warnings: {warning_count}")

        # Fallback summary
        if fallbacks:
            lines.append(f"Fallback Events: {len(fallbacks)}")
            fallback_reasons = {}
            for fallback in fallbacks:
                if fallback.reason not in fallback_reasons:
                    fallback_reasons[fallback.reason] = 0
                fallback_reasons[fallback.reason] += 1

            for reason, count in fallback_reasons.items():
                lines.append(f"  - {reason}: {count}")

        return "\n".join(lines)

    @staticmethod
    def get_user_message(run_status: str, diagnostics_count: int, fallbacks_count: int) -> str:
        """
        Generate user-facing message based on run status.

        Args:
            run_status: Status of run
            diagnostics_count: Number of diagnostics
            fallbacks_count: Number of fallback events

        Returns:
            User-facing message
        """
        if run_status == "completed":
            if fallbacks_count > 0:
                return f"Video generated successfully with {fallbacks_count} fallback(s). Some features may be degraded."
            else:
                return "Video generated successfully!"

        elif run_status == "failed":
            if diagnostics_count > 0:
                return f"Video generation failed. {diagnostics_count} error(s) occurred. Please check diagnostics."
            else:
                return "Video generation failed. Please try again."

        else:
            return f"Video generation in progress ({run_status})..."
