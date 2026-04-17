"""Media-related data models."""

from datetime import datetime
from typing import Optional, Tuple, Dict
from pydantic import BaseModel


class MediaFileMetadata(BaseModel):
    """Media file metadata."""
    file_path: str
    file_type: str  # 'video' or 'photo'
    file_size: int
    duration: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    creation_time: Optional[datetime] = None
    has_audio: Optional[bool] = None
    exif_data: Optional[Dict] = None
    indexed_at: datetime
