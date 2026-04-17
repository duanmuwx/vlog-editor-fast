"""Diagnostic reporting - aggregate diagnostics and fallback events."""

import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional
from src.shared.types import (
    DiagnosticBundle, DiagnosticEvent, RecoverySuggestion,
    ErrorType, PerformanceMetrics
)
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    DiagnosticRecord, FallbackEventRecord, RunRecord
)


class ErrorAnalyzer:
    """Analyzes errors and generates recovery suggestions."""

    ERROR_RECOVERY_MAP = {
        "RetryableError": {
            "type": ErrorType.RETRYABLE,
            "suggestions": [
                "Retry the operation",
                "Check network connectivity",
                "Verify API availability"
            ]
        },
        "ResourceError": {
            "type": ErrorType.RESOURCE,
            "suggestions": [
                "Enable lightweight mode",
                "Free up system memory",
                "Check disk space availability"
            ]
        },
        "ValidationError": {
            "type": ErrorType.VALIDATION,
            "suggestions": [
                "Check input data validity",
                "Verify file formats",
                "Review error details"
            ]
        },
        "DependencyError": {
            "type": ErrorType.DEPENDENCY,
            "suggestions": [
                "Regenerate upstream artifacts",
                "Verify version dependencies",
                "Check artifact validity"
            ]
        }
    }

    @staticmethod
    def analyze_error(error: Exception, context: Dict) -> Dict:
        """Analyze error and generate recovery suggestions."""
        error_type = type(error).__name__
        recovery_info = ErrorAnalyzer.ERROR_RECOVERY_MAP.get(
            error_type,
            {
                "type": ErrorType.MANUAL,
                "suggestions": ["Contact support", "Check logs for details"]
            }
        )

        return {
            "error_type": error_type,
            "error_message": str(error),
            "stage_name": context.get("stage_name", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "recovery_type": recovery_info["type"].value,
            "suggestions": recovery_info["suggestions"]
        }

    @staticmethod
    def generate_recovery_suggestions(error_analysis: Dict) -> List[RecoverySuggestion]:
        """Generate recovery suggestions from error analysis."""
        suggestions = []
        error_type = error_analysis.get("recovery_type", ErrorType.MANUAL.value)

        for idx, suggestion_text in enumerate(error_analysis.get("suggestions", [])):
            suggestions.append(
                RecoverySuggestion(
                    error_type=ErrorType(error_type),
                    suggestion=suggestion_text,
                    action="retry" if error_type == ErrorType.RETRYABLE.value else "manual_fix",
                    priority=5 - idx
                )
            )

        return suggestions


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
        """Generate user-facing message based on run status."""
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

    @staticmethod
    def generate_diagnostic_bundle(
        project_id: str,
        run_id: str,
        run_record,
        performance_metrics: Optional[Dict] = None
    ) -> DiagnosticBundle:
        """Generate complete diagnostic bundle for a run."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
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

            # Build error timeline
            error_timeline = []
            for diagnostic in diagnostics:
                if diagnostic.severity == "error":
                    error_timeline.append(
                        DiagnosticEvent(
                            event_id=diagnostic.diagnostic_id,
                            event_type="error",
                            stage_name=diagnostic.issue_type,
                            message=diagnostic.message,
                            timestamp=diagnostic.created_at
                        )
                    )

            # Generate recovery suggestions
            recovery_suggestions = []
            for error_event in error_timeline:
                analysis = ErrorAnalyzer.analyze_error(
                    Exception(error_event.message),
                    {"stage_name": error_event.stage_name}
                )
                recovery_suggestions.extend(
                    ErrorAnalyzer.generate_recovery_suggestions(analysis)
                )

            # Build run summary
            run_summary = {
                "run_id": run_id,
                "project_id": project_id,
                "status": run_record.status,
                "started_at": run_record.started_at.isoformat(),
                "ended_at": run_record.ended_at.isoformat() if run_record.ended_at else None,
                "total_diagnostics": len(diagnostics),
                "total_fallbacks": len(fallbacks),
                "error_count": sum(1 for d in diagnostics if d.severity == "error"),
                "warning_count": sum(1 for d in diagnostics if d.severity == "warning")
            }

            # Build performance metrics
            perf_metrics = None
            if performance_metrics:
                perf_metrics = PerformanceMetrics(
                    total_duration_seconds=performance_metrics.get("total_duration_seconds", 0),
                    stage_durations=performance_metrics.get("stage_durations", {}),
                    memory_peak_mb=performance_metrics.get("memory_peak_mb", 0),
                    disk_usage_mb=performance_metrics.get("disk_usage_mb", 0)
                )

            # Build diagnostic bundle
            bundle = DiagnosticBundle(
                run_id=run_id,
                project_id=project_id,
                run_summary=run_summary,
                error_timeline=error_timeline,
                recovery_suggestions=recovery_suggestions,
                performance_metrics=perf_metrics,
                runtime_logs=DiagnosticReporter._collect_logs(diagnostics, fallbacks),
                created_at=datetime.utcnow()
            )

            return bundle

        finally:
            session.close()

    @staticmethod
    def export_diagnostic_bundle(
        bundle: DiagnosticBundle,
        format: str = "json"
    ) -> str:
        """Export diagnostic bundle in specified format."""
        if format == "json":
            return json.dumps(bundle.dict(), indent=2, default=str)
        elif format == "markdown":
            return DiagnosticReporter._format_as_markdown(bundle)
        elif format == "html":
            return DiagnosticReporter._format_as_html(bundle)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _format_as_markdown(bundle: DiagnosticBundle) -> str:
        """Format diagnostic bundle as Markdown."""
        lines = [
            f"# Diagnostic Report - {bundle.run_id}",
            f"\n## Run Summary",
            f"- **Status**: {bundle.run_summary.get('status')}",
            f"- **Started**: {bundle.run_summary.get('started_at')}",
            f"- **Ended**: {bundle.run_summary.get('ended_at')}",
            f"- **Errors**: {bundle.run_summary.get('error_count')}",
            f"- **Warnings**: {bundle.run_summary.get('warning_count')}",
        ]

        if bundle.error_timeline:
            lines.append("\n## Errors")
            for event in bundle.error_timeline:
                lines.append(f"- **{event.stage_name}**: {event.message}")

        if bundle.recovery_suggestions:
            lines.append("\n## Recovery Suggestions")
            for suggestion in bundle.recovery_suggestions:
                lines.append(f"- **{suggestion.error_type.value}** (Priority {suggestion.priority}): {suggestion.suggestion}")

        if bundle.performance_metrics:
            lines.append("\n## Performance Metrics")
            lines.append(f"- **Total Duration**: {bundle.performance_metrics.total_duration_seconds:.2f}s")
            for stage, duration in bundle.performance_metrics.stage_durations.items():
                lines.append(f"  - {stage}: {duration:.2f}s")

        return "\n".join(lines)

    @staticmethod
    def _format_as_html(bundle: DiagnosticBundle) -> str:
        """Format diagnostic bundle as HTML."""
        html = f"""
        <html>
        <head><title>Diagnostic Report</title></head>
        <body>
        <h1>Diagnostic Report - {bundle.run_id}</h1>
        <h2>Run Summary</h2>
        <ul>
        <li>Status: {bundle.run_summary.get('status')}</li>
        <li>Started: {bundle.run_summary.get('started_at')}</li>
        <li>Ended: {bundle.run_summary.get('ended_at')}</li>
        <li>Errors: {bundle.run_summary.get('error_count')}</li>
        <li>Warnings: {bundle.run_summary.get('warning_count')}</li>
        </ul>
        """

        if bundle.error_timeline:
            html += "<h2>Errors</h2><ul>"
            for event in bundle.error_timeline:
                html += f"<li><strong>{event.stage_name}</strong>: {event.message}</li>"
            html += "</ul>"

        if bundle.recovery_suggestions:
            html += "<h2>Recovery Suggestions</h2><ul>"
            for suggestion in bundle.recovery_suggestions:
                html += f"<li><strong>{suggestion.error_type.value}</strong> (Priority {suggestion.priority}): {suggestion.suggestion}</li>"
            html += "</ul>"

        html += "</body></html>"
        return html

    @staticmethod
    def _collect_logs(diagnostics: List, fallbacks: List) -> str:
        """Collect logs from diagnostics and fallbacks."""
        lines = []
        for diagnostic in diagnostics:
            lines.append(f"[{diagnostic.created_at}] {diagnostic.severity.upper()}: {diagnostic.message}")
        for fallback in fallbacks:
            lines.append(f"[{fallback.created_at}] FALLBACK: {fallback.reason} -> {fallback.action}")
        return "\n".join(lines)

    @staticmethod
    def generate_recovery_manifest(bundle: DiagnosticBundle) -> Dict:
        """Generate recovery manifest to guide user recovery."""
        manifest = {
            "run_id": bundle.run_id,
            "status": bundle.run_summary.get("status"),
            "recovery_steps": [],
            "next_actions": []
        }

        if bundle.run_summary.get("error_count", 0) > 0:
            manifest["recovery_steps"].append({
                "step": 1,
                "action": "Review errors",
                "details": [e.message for e in bundle.error_timeline]
            })

            if bundle.recovery_suggestions:
                manifest["recovery_steps"].append({
                    "step": 2,
                    "action": "Apply recovery suggestions",
                    "suggestions": [
                        {
                            "priority": s.priority,
                            "action": s.action,
                            "description": s.suggestion
                        }
                        for s in sorted(bundle.recovery_suggestions, key=lambda x: x.priority, reverse=True)
                    ]
                })

                manifest["next_actions"].append("Retry failed stage")
                manifest["next_actions"].append("Regenerate affected artifacts")

        return manifest
