"""Database schema definitions."""

import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ProjectRecord(Base):
    """Projects table."""
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectConfigRecord(Base):
    """Project configs table."""
    __tablename__ = "project_configs"

    config_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), unique=True, nullable=False)
    travel_note = Column(String, nullable=False)
    bgm_asset = Column(String, nullable=True)
    tts_voice = Column(String, nullable=True)
    metadata_pack = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MediaFileRecord(Base):
    """Media files table."""
    __tablename__ = "media_files"

    file_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'video' or 'photo'
    file_size = Column(Integer, nullable=False)
    duration = Column(Float, nullable=True)
    resolution = Column(String, nullable=True)  # "1920x1080"
    creation_time = Column(DateTime, nullable=True)
    has_audio = Column(Boolean, nullable=True)
    exif_data = Column(JSON, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)


class ValidationReportRecord(Base):
    """Validation reports table."""
    __tablename__ = "validation_reports"

    report_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    is_valid = Column(Boolean, nullable=False)
    errors = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    media_summary = Column(JSON, nullable=True)
    metadata_coverage = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AssetIndexRecord(Base):
    """Asset indexes table."""
    __tablename__ = "asset_indexes"

    index_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), unique=True, nullable=False)
    total_videos = Column(Integer, default=0)
    total_photos = Column(Integer, default=0)
    total_duration = Column(Float, default=0.0)
    metadata_availability = Column(JSON, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)


class StorySkeletonRecord(Base):
    """Story skeletons table."""
    __tablename__ = "story_skeletons"

    skeleton_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), unique=True, nullable=False)
    version = Column(Integer, default=1)
    total_segments = Column(Integer, nullable=False)
    narrative_coverage = Column(Float, nullable=False)
    parsing_confidence = Column(Float, nullable=False)
    status = Column(String, default="draft")  # "draft", "confirmed"
    user_edits = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)


class StorySegmentRecord(Base):
    """Story segments table."""
    __tablename__ = "story_segments"

    segment_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    skeleton_id = Column(String, ForeignKey("story_skeletons.skeleton_id"), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    start_index = Column(Integer, nullable=False)
    end_index = Column(Integer, nullable=False)
    importance = Column(String, nullable=False)  # "high", "medium", "low"
    confidence = Column(Float, nullable=False)
    keywords = Column(JSON, nullable=True)
    locations = Column(JSON, nullable=True)
    timestamps = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SkeletonConfirmationRecord(Base):
    """Skeleton confirmations table."""
    __tablename__ = "skeleton_confirmations"

    confirmation_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    skeleton_id = Column(String, ForeignKey("story_skeletons.skeleton_id"), nullable=False)
    edits = Column(JSON, nullable=False)
    confirmed_at = Column(DateTime, default=datetime.utcnow)


class MediaShotRecord(Base):
    """Media shots table."""
    __tablename__ = "media_shots"

    shot_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    file_id = Column(String, ForeignKey("media_files.file_id"), nullable=False)
    shot_type = Column(String, nullable=False)  # "video_shot", "photo"
    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=False)
    has_audio = Column(Boolean, nullable=False)
    visual_features = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MediaAnalysisRecord(Base):
    """Media analysis table."""
    __tablename__ = "media_analysis"

    analysis_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), unique=True, nullable=False)
    total_shots = Column(Integer, nullable=False)
    analysis_status = Column(String, nullable=False)  # "completed", "partial", "degraded"
    created_at = Column(DateTime, default=datetime.utcnow)


class AlignmentCandidateRecord(Base):
    """Alignment candidates table."""
    __tablename__ = "alignment_candidates"

    candidate_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    segment_id = Column(String, ForeignKey("story_segments.segment_id"), nullable=False)
    shot_id = Column(String, ForeignKey("media_shots.shot_id"), nullable=False)
    match_score = Column(Float, nullable=False)
    text_match_score = Column(Float, nullable=False)
    time_match_score = Column(Float, nullable=True)
    location_match_score = Column(Float, nullable=True)
    reasoning = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class HighlightSelectionRecord(Base):
    """Highlight selections table."""
    __tablename__ = "highlight_selections"

    selection_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    segment_id = Column(String, ForeignKey("story_segments.segment_id"), unique=True, nullable=False)
    selected_shot_id = Column(String, ForeignKey("media_shots.shot_id"), nullable=False)
    user_confirmed = Column(Boolean, nullable=False)
    alternatives_available = Column(Integer, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Phase 4: Final Composition & Export

class TimelineRecord(Base):
    """Timelines table."""
    __tablename__ = "timelines"

    timeline_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    version_id = Column(String, unique=True, nullable=False)
    total_duration_seconds = Column(Float, nullable=False)
    target_duration_seconds = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TimelineSegmentRecord(Base):
    """Timeline segments table."""
    __tablename__ = "timeline_segments"

    segment_id = Column(String, primary_key=True)
    timeline_id = Column(String, ForeignKey("timelines.timeline_id"), nullable=False)
    story_segment_id = Column(String, ForeignKey("story_segments.segment_id"), nullable=False)
    narration_start = Column(Float, nullable=False)
    narration_end = Column(Float, nullable=False)
    total_duration = Column(Float, nullable=False)


class TimelineClipRecord(Base):
    """Timeline clips table."""
    __tablename__ = "timeline_clips"

    clip_id = Column(String, primary_key=True)
    segment_id = Column(String, ForeignKey("timeline_segments.segment_id"), nullable=False)
    shot_id = Column(String, ForeignKey("media_shots.shot_id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    transition = Column(String, nullable=False)  # "cut", "fade", "dissolve"


class NarrationRecord(Base):
    """Narrations table."""
    __tablename__ = "narrations"

    narration_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    version_id = Column(String, unique=True, nullable=False)
    narration_text = Column(String, nullable=False)
    tts_audio_path = Column(String, nullable=False)
    tts_voice = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubtitleRecord(Base):
    """Subtitles table."""
    __tablename__ = "subtitles"

    subtitle_id = Column(String, primary_key=True)
    narration_id = Column(String, ForeignKey("narrations.narration_id"), nullable=False)
    text = Column(String, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)


class TextCardRecord(Base):
    """Text cards table."""
    __tablename__ = "text_cards"

    card_id = Column(String, primary_key=True)
    narration_id = Column(String, ForeignKey("narrations.narration_id"), nullable=False)
    text = Column(String, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    position = Column(String, nullable=False)  # "center", "top", "bottom"


class AudioMixRecord(Base):
    """Audio mixes table."""
    __tablename__ = "audio_mixes"

    audio_mix_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    version_id = Column(String, unique=True, nullable=False)
    mixed_audio_path = Column(String, nullable=False)
    total_duration_seconds = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AudioTrackRecord(Base):
    """Audio tracks table."""
    __tablename__ = "audio_tracks"

    track_id = Column(String, primary_key=True)
    audio_mix_id = Column(String, ForeignKey("audio_mixes.audio_mix_id"), nullable=False)
    track_type = Column(String, nullable=False)  # "narration", "ambient", "bgm"
    file_path = Column(String, nullable=False)
    volume = Column(Float, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)


class ExportRecord(Base):
    """Exports table."""
    __tablename__ = "exports"

    export_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    version_id = Column(String, unique=True, nullable=False)
    video_path = Column(String, nullable=False)
    subtitle_path = Column(String, nullable=False)
    narration_path = Column(String, nullable=False)
    manifest_path = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "success", "partial", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)


class ArtifactVersionRecord(Base):
    """Artifact versions table."""
    __tablename__ = "artifact_versions"

    version_id = Column(String, primary_key=True)
    artifact_type = Column(String, nullable=False)  # "timeline", "narration", "audio_mix", "export"
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    upstream_versions = Column(JSON, nullable=True)  # Dependencies
    status = Column(String, nullable=False)  # "active", "superseded", "invalidated"
    created_at = Column(DateTime, default=datetime.utcnow)
    invalidated_at = Column(DateTime, nullable=True)


class RunRecord(Base):
    """Run records table."""
    __tablename__ = "run_records"

    run_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)


class TaskStateRecord(Base):
    """Task states table."""
    __tablename__ = "task_states"

    task_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("run_records.run_id"), nullable=False)
    stage_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)


class DiagnosticRecord(Base):
    """Diagnostics table."""
    __tablename__ = "diagnostics"

    diagnostic_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    run_id = Column(String, ForeignKey("run_records.run_id"), nullable=False)
    issue_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class FallbackEventRecord(Base):
    """Fallback events table."""
    __tablename__ = "fallback_events"

    event_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    run_id = Column(String, ForeignKey("run_records.run_id"), nullable=False)
    reason = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)