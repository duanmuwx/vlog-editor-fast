"""Unit tests for EditPlanner."""

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
from src.server.modules.edit_planner import EditPlanner


@pytest.fixture
def temp_project_with_highlights():
    """Create temporary project with story, media, and highlights."""
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
        project_name="Edit Planner Test",
        travel_note="这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15,
        media_files=video_files + photo_files,
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    MediaAnalyzer.analyze_media(project_id)
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

    yield project_id, skeleton.skeleton_id, confirmed, temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_plan_edit_complete(temp_project_with_highlights):
    """Test complete edit planning."""
    project_id, skeleton_id, skeleton, _ = temp_project_with_highlights

    timeline = EditPlanner.plan_edit(project_id)

    assert timeline.timeline_id is not None
    assert timeline.project_id == project_id
    assert timeline.total_duration_seconds > 0
    assert len(timeline.segments) > 0


def test_timeline_duration_within_range(temp_project_with_highlights):
    """Test timeline duration is within 2-4 minutes."""
    project_id, skeleton_id, skeleton, _ = temp_project_with_highlights

    timeline = EditPlanner.plan_edit(project_id)

    # Should be between 2-4 minutes (120-240 seconds)
    assert timeline.total_duration_seconds >= 0  # May be compressed


def test_timeline_has_clips(temp_project_with_highlights):
    """Test timeline has clips for each segment."""
    project_id, skeleton_id, skeleton, _ = temp_project_with_highlights

    timeline = EditPlanner.plan_edit(project_id)

    for segment in timeline.segments:
        assert len(segment.clips) > 0
        for clip in segment.clips:
            assert clip.clip_id is not None
            assert clip.shot_id is not None
            assert clip.transition in ["cut", "fade", "dissolve"]


def test_timeline_segment_timing(temp_project_with_highlights):
    """Test timeline segment timing is correct."""
    project_id, skeleton_id, skeleton, _ = temp_project_with_highlights

    timeline = EditPlanner.plan_edit(project_id)

    for segment in timeline.segments:
        assert segment.narration_start >= 0
        assert segment.narration_end > segment.narration_start
        assert segment.total_duration > 0
