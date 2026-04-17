"""Unit tests for HighlightConfirmation."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser
from src.server.modules.skeleton_confirmation import SkeletonConfirmation
from src.server.modules.media_analyzer import MediaAnalyzer
from src.server.modules.alignment_engine import AlignmentEngine
from src.server.modules.highlight_confirmation import HighlightConfirmation


@pytest.fixture
def temp_project_with_highlights():
    """Create temporary project with story, media, and alignment."""
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
        project_name="Highlight Test",
        travel_note="这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15,
        media_files=video_files + photo_files,
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    MediaAnalyzer.analyze_media(project_id)
    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)

    yield project_id, skeleton.skeleton_id, confirmed, candidates, temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_confirm_highlights_valid(temp_project_with_highlights):
    """Test confirming highlights with valid selections."""
    project_id, skeleton_id, skeleton, candidates, _ = temp_project_with_highlights

    selections = []
    for segment in skeleton.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        confirmed = HighlightConfirmation.confirm_highlights(project_id, skeleton_id, selections)

        assert len(confirmed) == len(selections)
        assert all(h.user_confirmed for h in confirmed)
        assert all(h.confirmed_at is not None for h in confirmed)


def test_confirm_highlights_invalid_shot(temp_project_with_highlights):
    """Test confirming highlights with invalid shot ID."""
    project_id, skeleton_id, skeleton, candidates, _ = temp_project_with_highlights

    selections = [
        {
            "segment_id": skeleton.segments[0].segment_id,
            "shot_id": "invalid_shot_id",
            "user_confirmed": True
        }
    ]

    with pytest.raises(ValueError):
        HighlightConfirmation.confirm_highlights(project_id, skeleton_id, selections)


def test_confirm_highlights_missing_segment(temp_project_with_highlights):
    """Test confirming highlights with missing segment."""
    project_id, skeleton_id, skeleton, candidates, _ = temp_project_with_highlights

    selections = [
        {
            "segment_id": skeleton.segments[0].segment_id,
            "shot_id": candidates[0].shot_id,
            "user_confirmed": True
        }
    ]

    with pytest.raises(ValueError):
        HighlightConfirmation.confirm_highlights(project_id, skeleton_id, selections)


def test_get_current_highlights(temp_project_with_highlights):
    """Test retrieving current highlights."""
    project_id, skeleton_id, skeleton, candidates, _ = temp_project_with_highlights

    selections = []
    for segment in skeleton.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        HighlightConfirmation.confirm_highlights(project_id, skeleton_id, selections)

        retrieved = HighlightConfirmation.get_current_highlights(project_id)

        assert retrieved is not None
        assert len(retrieved) == len(selections)
        assert all(h.user_confirmed for h in retrieved)


def test_get_current_highlights_none():
    """Test retrieving highlights when none exist."""
    temp_dir = tempfile.mkdtemp()

    input_contract = ProjectInputContract(
        project_name="Empty Highlights Test",
        travel_note="测试游记。" * 50,
        media_files=[],
    )

    project_id = ProjectManager.create_project(input_contract)

    retrieved = HighlightConfirmation.get_current_highlights(project_id)

    assert retrieved is None

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
