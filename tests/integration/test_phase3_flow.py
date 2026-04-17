"""Integration tests for Phase 3 flow."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser
from src.server.modules.story_skeleton import StorySkeleton
from src.server.modules.skeleton_confirmation import SkeletonConfirmation
from src.server.modules.media_analyzer import MediaAnalyzer
from src.server.modules.alignment_engine import AlignmentEngine
from src.server.modules.highlight_confirmation import HighlightConfirmation


@pytest.fixture
def temp_project_media():
    """Create temporary project with media files."""
    temp_dir = tempfile.mkdtemp()

    video_files = []
    for i in range(3):
        video_path = os.path.join(temp_dir, f"video_{i}.mp4")
        Path(video_path).write_bytes(b"dummy video content")
        video_files.append(video_path)

    photo_files = []
    for i in range(20):
        photo_path = os.path.join(temp_dir, f"photo_{i}.jpg")
        Path(photo_path).write_bytes(b"dummy photo content")
        photo_files.append(photo_path)

    yield {
        "temp_dir": temp_dir,
        "videos": video_files,
        "photos": photo_files,
        "all_files": video_files + photo_files
    }

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_complete_phase3_flow(temp_project_media):
    """Test complete Phase 3 flow: analyze → align → confirm."""
    media_files = temp_project_media["all_files"]

    input_contract = ProjectInputContract(
        project_name="Phase 3 Test Project",
        travel_note="这是第一天的故事。我们到达了北京。" * 20
                    + "这是第二天的故事。我们参观了长城。" * 20
                    + "这是第三天的故事。我们游览了故宫。" * 20,
        media_files=media_files,
    )

    project_id = ProjectManager.create_project(input_contract)
    assert project_id is not None

    config = ProjectManager.get_project_config(project_id)
    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    assert skeleton.total_segments >= 3

    confirmed_skeleton = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])
    assert confirmed_skeleton.status == "confirmed"

    analysis = MediaAnalyzer.analyze_media(project_id)
    assert analysis.total_shots >= 0
    assert analysis.analysis_status in ["completed", "partial", "degraded"]

    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)
    assert len(candidates) > 0

    selections = []
    for segment in confirmed_skeleton.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        confirmed_highlights = HighlightConfirmation.confirm_highlights(
            project_id, skeleton.skeleton_id, selections
        )
        assert len(confirmed_highlights) == len(selections)
        assert all(h.user_confirmed for h in confirmed_highlights)

        retrieved_highlights = HighlightConfirmation.get_current_highlights(project_id)
        assert retrieved_highlights is not None
        assert len(retrieved_highlights) == len(selections)


def test_phase3_media_analysis(temp_project_media):
    """Test media analysis independently."""
    media_files = temp_project_media["all_files"]

    input_contract = ProjectInputContract(
        project_name="Media Analysis Test",
        travel_note="测试游记。" * 50,
        media_files=media_files,
    )

    project_id = ProjectManager.create_project(input_contract)

    analysis = MediaAnalyzer.analyze_media(project_id)

    assert analysis.analysis_id is not None
    assert analysis.project_id == project_id
    assert analysis.total_shots >= 0
    assert analysis.analysis_status in ["completed", "partial", "degraded"]


def test_phase3_alignment_with_skeleton(temp_project_media):
    """Test alignment with confirmed skeleton."""
    media_files = temp_project_media["all_files"]

    input_contract = ProjectInputContract(
        project_name="Alignment Test",
        travel_note="这是第一段。" * 15 + "这是第二段。" * 15 + "这是第三段。" * 15,
        media_files=media_files,
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    MediaAnalyzer.analyze_media(project_id)

    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)

    assert len(candidates) > 0

    for segment in confirmed.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        assert len(segment_candidates) > 0
        assert all(0.0 <= c.match_score <= 1.0 for c in segment_candidates)


def test_phase3_highlight_confirmation_validation(temp_project_media):
    """Test highlight confirmation validation."""
    media_files = temp_project_media["all_files"]

    input_contract = ProjectInputContract(
        project_name="Highlight Validation Test",
        travel_note="这是第一段。" * 15 + "这是第二段。" * 15 + "这是第三段。" * 15,
        media_files=media_files,
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    MediaAnalyzer.analyze_media(project_id)
    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)

    invalid_selections = [
        {
            "segment_id": confirmed.segments[0].segment_id,
            "shot_id": "invalid_shot_id",
            "user_confirmed": True
        }
    ]

    with pytest.raises(ValueError):
        HighlightConfirmation.confirm_highlights(project_id, skeleton.skeleton_id, invalid_selections)

    incomplete_selections = [
        {
            "segment_id": confirmed.segments[0].segment_id,
            "shot_id": candidates[0].shot_id,
            "user_confirmed": True
        }
    ]

    with pytest.raises(ValueError):
        HighlightConfirmation.confirm_highlights(project_id, skeleton.skeleton_id, incomplete_selections)
