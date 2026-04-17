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
    STORY_PARSED = "story_parsed"
    SKELETON_CONFIRMED = "skeleton_confirmed"
    MEDIA_ANALYZED = "media_analyzed"
    MEDIA_ALIGNED = "media_aligned"
    HIGHLIGHTS_CONFIRMED = "highlights_confirmed"
    EDIT_PLANNED = "edit_planned"
    NARRATION_GENERATED = "narration_generated"
    AUDIO_MIXED = "audio_mixed"
    EXPORTED = "exported"
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


class StorySegment(BaseModel):
    """Story segment from narrative parsing."""
    segment_id: str
    title: str
    summary: str
    start_index: int  # Character index in narrative
    end_index: int  # Character index in narrative
    importance: str  # "high", "medium", "low"
    confidence: float  # 0.0-1.0 parsing confidence
    keywords: List[str] = []
    locations: List[str] = []
    timestamps: List[str] = []


class StorySkeleton(BaseModel):
    """Story skeleton with versioning."""
    skeleton_id: str
    project_id: str
    version: int
    segments: List[StorySegment]
    total_segments: int
    narrative_coverage: float  # 0.0-1.0
    parsing_confidence: float  # 0.0-1.0
    status: str  # "draft", "confirmed"
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    user_edits: Optional[Dict] = None


class MediaShot(BaseModel):
    """Media shot from video or photo."""
    shot_id: str
    file_id: str
    shot_type: str  # "video_shot", "photo"
    start_time: Optional[float] = None  # For videos: start time in seconds
    end_time: Optional[float] = None  # For videos: end time in seconds
    duration: Optional[float] = None  # For videos: duration in seconds
    quality_score: float  # 0.0-1.0
    has_audio: bool
    visual_features: Dict = {}  # Scene labels, objects, people, etc.
    confidence: float  # 0.0-1.0 detection confidence


class MediaAnalysis(BaseModel):
    """Media analysis results."""
    analysis_id: str
    project_id: str
    shots: List[MediaShot]
    total_shots: int
    analysis_status: str  # "completed", "partial", "degraded"
    created_at: datetime


class AlignmentCandidate(BaseModel):
    """Candidate shot for a story segment."""
    candidate_id: str
    segment_id: str
    shot_id: str
    match_score: float  # 0.0-1.0 overall match confidence
    text_match_score: float  # Text-visual semantic match
    time_match_score: Optional[float] = None  # Time-based match
    location_match_score: Optional[float] = None  # Location-based match
    reasoning: str  # Why this shot matches this segment


class HighlightSelection(BaseModel):
    """User's highlight selection for a segment."""
    selection_id: str
    project_id: str
    segment_id: str
    selected_shot_id: str
    user_confirmed: bool
    alternatives_available: int
    confirmed_at: Optional[datetime] = None

class SkeletonConfirmationRequest(BaseModel):
    """User confirmation request for skeleton."""
    skeleton_id: str
    edits: List[Dict] = []  # List of edit operations


# Phase 4: Final Composition & Export

class TimelineClip(BaseModel):
    """Clip in timeline segment."""
    clip_id: str
    shot_id: str
    start_time: float  # Seconds in timeline
    end_time: float  # Seconds in timeline
    transition: str  # "cut", "fade", "dissolve"
    duration: float  # Calculated as end_time - start_time


class TimelineSegment(BaseModel):
    """Segment in timeline."""
    segment_id: str  # Reference to StorySegment
    clips: List[TimelineClip]
    narration_start: float  # When narration starts
    narration_end: float  # When narration ends
    total_duration: float  # Total segment duration


class Timeline(BaseModel):
    """Executable timeline with clips and timing."""
    timeline_id: str
    project_id: str
    version_id: str
    segments: List[TimelineSegment]
    total_duration_seconds: float
    target_duration_seconds: float
    created_at: datetime


class Subtitle(BaseModel):
    """Subtitle entry."""
    subtitle_id: str
    text: str
    start_time: float  # Seconds
    end_time: float  # Seconds


class TextCard(BaseModel):
    """Text card for display."""
    card_id: str
    text: str
    duration_seconds: float
    position: str  # "center", "top", "bottom"


class NarrationPack(BaseModel):
    """Narration pack with TTS audio and subtitles."""
    narration_id: str
    project_id: str
    version_id: str
    narration_text: str
    tts_audio_path: str
    subtitles: List[Subtitle]
    text_cards: List[TextCard]
    tts_voice: str
    created_at: datetime


class AudioTrack(BaseModel):
    """Audio track in mix."""
    track_id: str
    track_type: str  # "narration", "ambient", "bgm"
    file_path: str
    volume: float  # 0.0-1.0
    start_time: float
    end_time: float


class AudioMixPack(BaseModel):
    """Mixed audio pack with all tracks."""
    audio_mix_id: str
    project_id: str
    version_id: str
    tracks: List[AudioTrack]
    mixed_audio_path: str
    total_duration_seconds: float
    created_at: datetime


class ExportBundle(BaseModel):
    """Final export bundle with all outputs."""
    export_id: str
    project_id: str
    version_id: str
    video_path: str
    subtitle_path: str
    narration_path: str
    manifest_path: str
    status: str  # "success", "partial", "failed"
    created_at: datetime


class ArtifactVersion(BaseModel):
    """Version metadata with dependency tracking."""
    version_id: str
    artifact_type: str  # "timeline", "narration", "audio_mix", "export"
    project_id: str
    upstream_versions: Dict[str, str] = {}  # Dependencies
    status: str  # "active", "superseded", "invalidated"
    created_at: datetime
    invalidated_at: Optional[datetime] = None
