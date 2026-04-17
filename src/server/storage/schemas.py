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

