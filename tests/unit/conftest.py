"""Shared fixtures for unit tests."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser
from src.server.modules.skeleton_confirmation import SkeletonConfirmation
from src.server.modules.alignment_engine import AlignmentEngine
from src.server.modules.highlight_confirmation import HighlightConfirmation
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import MediaShotRecord


def create_test_project_with_highlights(project_name: str, travel_note: str):
    """Helper to create a test project with highlights."""
    temp_dir = tempfile.mkdtemp()

    video_files = []
    for i in range(2):
        video_path = os.path.join(temp_dir, f"video_{i}.mp4")
        Path(video_path).write_bytes(b"dummy video content")
        video_files.append(video_path)

    photo_files = []
    for i in range(10):
        photo_path = os.path.join(temp_dir, f"photo_{i}.jpg")
        Path(photo_path).write_bytes(b"dummy photo content")
        photo_files.append(photo_path)

    input_contract = ProjectInputContract(
        project_name=project_name,
        travel_note=travel_note,
        media_files=video_files + photo_files,
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    # Insert test media shots directly into database
    db = get_or_create_db(project_id)
    session = db.get_session()

    try:
        for i in range(12):
            shot = MediaShotRecord(
                shot_id=f"shot_{i}",
                file_id=f"file_{i}",
                project_id=project_id,
                shot_type="photo" if i < 10 else "video_shot",
                start_time=None if i < 10 else float(i),
                end_time=None if i < 10 else float(i + 1),
                duration=None if i < 10 else 1.0,
                quality_score=0.8,
                has_audio=False,
                visual_features={"scene_type": "outdoor", "dominant_color": "blue"},
                confidence=0.9,
                created_at=datetime.utcnow(),
            )
            session.add(shot)
        session.commit()
    finally:
        session.close()

    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)

    selections = []
    for segment in confirmed.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        HighlightConfirmation.confirm_highlights(project_id, skeleton.skeleton_id, selections)

    return project_id, skeleton.skeleton_id, confirmed, temp_dir


def add_media_shots_to_project(project_id: str, num_shots: int = 12):
    """Helper to add media shots to an existing project."""
    db = get_or_create_db(project_id)
    session = db.get_session()

    try:
        for i in range(num_shots):
            shot = MediaShotRecord(
                shot_id=f"shot_{i}",
                file_id=f"file_{i}",
                project_id=project_id,
                shot_type="photo" if i < 10 else "video_shot",
                start_time=None if i < 10 else float(i),
                end_time=None if i < 10 else float(i + 1),
                duration=None if i < 10 else 1.0,
                quality_score=0.8,
                has_audio=False,
                visual_features={"scene_type": "outdoor", "dominant_color": "blue"},
                confidence=0.9,
                created_at=datetime.utcnow(),
            )
            session.add(shot)
        session.commit()
    finally:
        session.close()
