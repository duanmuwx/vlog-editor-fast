"""Input Validator module."""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
import uuid

from src.shared.types import ProjectInputContract, InputValidationReport, FileType
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import ValidationReportRecord


class InputValidator:
    """Validates project input."""

    # Validation thresholds
    MIN_NARRATIVE_LENGTH = 150
    MIN_VIDEO_COUNT = 5
    MIN_PHOTO_COUNT = 50
    MIN_TOTAL_DURATION = 600  # 10 minutes in seconds

    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'}
    SUPPORTED_PHOTO_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

    @staticmethod
    def validate(project_id: str, input_contract: ProjectInputContract) -> InputValidationReport:
        """Execute complete input validation."""
        errors = []
        warnings = []
        recommendations = []

        # Check narrative
        narrative_valid, narrative_msg = InputValidator.check_narrative_length(
            input_contract.travel_note
        )
        if not narrative_valid:
            errors.append(narrative_msg)
        elif len(input_contract.travel_note) < InputValidator.MIN_NARRATIVE_LENGTH * 1.5:
            warnings.append(narrative_msg)

        # Check media files
        files_valid, file_errors = InputValidator.check_media_files(input_contract.media_files)
        errors.extend(file_errors)

        # Analyze media
        media_summary = InputValidator.analyze_media_files(input_contract.media_files)
        if media_summary['total_videos'] < InputValidator.MIN_VIDEO_COUNT:
            warnings.append(f"Video count ({media_summary['total_videos']}) is below recommended minimum ({InputValidator.MIN_VIDEO_COUNT})")
        if media_summary['total_photos'] < InputValidator.MIN_PHOTO_COUNT:
            warnings.append(f"Photo count ({media_summary['total_photos']}) is below recommended minimum ({InputValidator.MIN_PHOTO_COUNT})")
        if media_summary['total_duration'] < InputValidator.MIN_TOTAL_DURATION:
            errors.append(f"Total video duration ({media_summary['total_duration']:.0f}s) is below minimum ({InputValidator.MIN_TOTAL_DURATION}s)")

        # Analyze metadata coverage
        metadata_coverage = InputValidator.analyze_metadata_coverage(input_contract.media_files)

        # Generate recommendations
        if metadata_coverage['exif_coverage'] < 0.5:
            recommendations.append("Consider adding EXIF data to photos for better alignment")
        if metadata_coverage['gps_coverage'] < 0.3:
            recommendations.append("GPS data would improve location-based alignment")

        is_valid = len(errors) == 0

        report = InputValidationReport(
            project_id=project_id,
            is_valid=is_valid,
            validation_timestamp=datetime.utcnow(),
            errors=errors,
            warnings=warnings,
            media_summary=media_summary,
            metadata_coverage=metadata_coverage,
            recommendations=recommendations
        )

        # Save report to database
        InputValidator._save_validation_report(project_id, report)

        return report

    @staticmethod
    def check_narrative_length(text: str) -> Tuple[bool, str]:
        """Check narrative length."""
        length = len(text.strip())
        if length < InputValidator.MIN_NARRATIVE_LENGTH:
            return False, f"Narrative too short ({length} chars, minimum {InputValidator.MIN_NARRATIVE_LENGTH})"
        return True, ""

    @staticmethod
    def check_media_files(file_paths: List[str]) -> Tuple[bool, List[str]]:
        """Check media files existence and format."""
        errors = []

        if not file_paths:
            errors.append("No media files provided")
            return False, errors

        for file_path in file_paths:
            if not os.path.exists(file_path):
                errors.append(f"File not found: {file_path}")
                continue

            if not os.path.isfile(file_path):
                errors.append(f"Not a file: {file_path}")
                continue

            ext = Path(file_path).suffix.lower()
            if ext not in InputValidator.SUPPORTED_VIDEO_FORMATS and ext not in InputValidator.SUPPORTED_PHOTO_FORMATS:
                errors.append(f"Unsupported file format: {ext}")

        return len(errors) == 0, errors

    @staticmethod
    def analyze_media_files(file_paths: List[str]) -> Dict:
        """Analyze media files and return summary."""
        videos = []
        photos = []
        total_size = 0
        total_duration = 0.0

        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            ext = Path(file_path).suffix.lower()
            file_size = os.path.getsize(file_path)
            total_size += file_size

            if ext in InputValidator.SUPPORTED_VIDEO_FORMATS:
                videos.append(file_path)
                # Try to get video duration (simplified - would use ffprobe in real implementation)
                total_duration += 30.0  # placeholder
            elif ext in InputValidator.SUPPORTED_PHOTO_FORMATS:
                photos.append(file_path)

        return {
            'total_files': len(file_paths),
            'total_videos': len(videos),
            'total_photos': len(photos),
            'total_size_mb': total_size / (1024 * 1024),
            'total_duration': total_duration,
            'avg_video_duration': total_duration / len(videos) if videos else 0,
            'avg_photo_size_mb': (total_size / len(photos) / (1024 * 1024)) if photos else 0
        }

    @staticmethod
    def analyze_metadata_coverage(file_paths: List[str]) -> Dict:
        """Analyze metadata coverage."""
        # Simplified implementation - would check EXIF, GPS, timestamps in real implementation
        return {
            'exif_coverage': 0.3,  # placeholder
            'gps_coverage': 0.1,   # placeholder
            'timestamp_coverage': 0.5,  # placeholder
            'audio_coverage': 0.4  # placeholder
        }

    @staticmethod
    def _save_validation_report(project_id: str, report: InputValidationReport) -> None:
        """Save validation report to database."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            report_record = ValidationReportRecord(
                report_id=str(uuid.uuid4()),
                project_id=project_id,
                is_valid=report.is_valid,
                errors=report.errors,
                warnings=report.warnings,
                media_summary=report.media_summary,
                metadata_coverage=report.metadata_coverage,
                recommendations=report.recommendations,
                created_at=report.validation_timestamp
            )
            session.add(report_record)
            session.commit()
        finally:
            session.close()
