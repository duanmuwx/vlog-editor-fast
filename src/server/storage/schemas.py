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
