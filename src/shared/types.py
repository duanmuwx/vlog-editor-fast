"""Shared data types and constants."""

from enum import Enum
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from pydantic import BaseModel


class FileType(str, Enum):
    """Media file types."""
    VIDEO = "video"
    PHOTO = "photo"


class ProjectStatus(str, Enum):
    """Project status states."""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    AWAITING_USER = "awaiting_user"
    COMPLETED = "completed"
    FAILED = "failed"


class MediaFileInfo(BaseModel):
    """Media file metadata."""
    file_path: str
    file_type: FileType
    file_size: int
    duration: Optional[float] = None  # seconds for videos
    resolution: Optional[Tuple[int, int]] = None
    creation_time: Optional[datetime] = None
    has_audio: Optional[bool] = None
    exif_data: Optional[Dict] = None


class ProjectInputContract(BaseModel):
    """Project input contract."""
    project_name: str
    travel_note: str
    media_files: List[str]  # file paths
    bgm_asset: Optional[str] = None
    tts_voice: Optional[str] = None
    metadata_pack: Optional[Dict] = None


class InputValidationReport(BaseModel):
    """Input validation report."""
    project_id: str
    is_valid: bool
    validation_timestamp: datetime
    errors: List[str]
    warnings: List[str]
    media_summary: Dict
    metadata_coverage: Dict
    recommendations: List[str]


class AssetIndex(BaseModel):
    """Asset index."""
    project_id: str
    total_videos: int
    total_photos: int
    total_duration: float  # seconds
    indexed_at: datetime
    media_items: List[MediaFileInfo]
    metadata_availability: Dict
