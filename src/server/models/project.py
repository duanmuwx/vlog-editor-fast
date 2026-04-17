"""Project-related data models."""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class ProjectConfig(BaseModel):
    """Project configuration."""
    project_id: str
    travel_note: str
    bgm_asset: Optional[str] = None
    tts_voice: Optional[str] = None
    metadata_pack: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime


class ProjectMetadata(BaseModel):
    """Project metadata."""
    project_id: str
    project_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    total_videos: int = 0
    total_photos: int = 0
    total_duration: float = 0.0
