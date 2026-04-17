"""Validation-related data models."""

from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel


class ValidationError(BaseModel):
    """Validation error."""
    code: str
    message: str
    field: str


class ValidationWarning(BaseModel):
    """Validation warning."""
    code: str
    message: str
    field: str


class MediaSummary(BaseModel):
    """Media summary statistics."""
    total_files: int
    total_videos: int
    total_photos: int
    total_size_mb: float
    total_duration_minutes: float
    avg_video_duration: float
    avg_photo_size_mb: float


class MetadataCoverage(BaseModel):
    """Metadata coverage statistics."""
    exif_coverage: float  # percentage
    gps_coverage: float
    timestamp_coverage: float
    audio_coverage: float
