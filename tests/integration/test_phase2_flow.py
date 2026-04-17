"""Integration tests for Phase 2 flow."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser
from src.server.modules.story_skeleton import StorySkeleton
from src.server.modules.skeleton_confirmation import SkeletonConfirmation


@pytest.fixture
def temp_project_media():
    """Create temporary project with media files."""
    temp_dir = tempfile.mkdtemp()

    # Create video files
    video_files = []
    for i in range(5):
        video_path = os.path.join(temp_dir, f"video_{i}.mp4")
        Path(video_path).write_bytes(b"dummy video content")
        video_files.append(video_path)

    # Create photo files
    photo_files = []
    for i in range(50):
        photo_path = os.path.join(temp_dir, f"photo_{i}.jpg")
        Path(photo_path).write_bytes(b"dummy photo content")
        photo_files.append(photo_path)

    yield {
        "temp_dir": temp_dir,
        "videos": video_files,
        "photos": photo_files,
        "all_files": video_files + photo_files
    }

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_complete_phase2_flow(temp_project_media):
    """Test complete Phase 2 flow: parse → generate → confirm."""
    media_files = temp_project_media["all_files"]

    # Step 1: Create project
    input_contract = ProjectInputContract(
        project_name="Travel Vlog Project",
        travel_note="这是第一天的故事。我们到达了北京。" * 20
                    + "这是第二天的故事。我们参观了长城。" * 20
                    + "这是第三天的故事。我们游览了故宫。" * 20
                    + "这是第四天的故事。我们品尝了美食。" * 20,
        media_files=media_files,
        bgm_asset="bgm.mp3",
        tts_voice="female"
    )

    project_id = ProjectManager.create_project(input_contract)
    assert project_id is not None

    # Step 2: Parse story
    config = ProjectManager.get_project_config(project_id)
    skeleton = StoryParser.parse_story(project_id, config.travel_note)

    assert skeleton is not None
    assert skeleton.project_id == project_id
    assert 3 <= skeleton.total_segments <= 8
    assert skeleton.status == "draft"

    # Step 3: Retrieve skeleton
    retrieved_skeleton = StorySkeleton.get_skeleton(project_id, skeleton.skeleton_id)
    assert retrieved_skeleton is not None
    assert retrieved_skeleton.skeleton_id == skeleton.skeleton_id
    assert len(retrieved_skeleton.segments) == skeleton.total_segments

    # Step 4: Confirm skeleton without edits
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    assert confirmed.status == "confirmed"
    assert confirmed.confirmed_at is not None
    assert confirmed.total_segments == skeleton.total_segments

    # Step 5: Verify project status updated
    metadata = ProjectManager.get_project_metadata(project_id)
    assert metadata.status == "skeleton_confirmed"

    # Step 6: Get current skeleton
    current = StorySkeleton.get_current_skeleton(project_id)
    assert current is not None
    assert current.status == "confirmed"
    assert current.skeleton_id == skeleton.skeleton_id


def test_phase2_flow_with_edits(temp_project_media):
    """Test Phase 2 flow with user edits."""
    media_files = temp_project_media["all_files"]

    input_contract = ProjectInputContract(
        project_name="Travel Vlog Project",
        travel_note="这是第一段。" * 15 + "这是第二段。" * 15 + "这是第三段。" * 15 + "这是第四段。" * 15,
        media_files=media_files
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    # Parse story
    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    initial_count = skeleton.total_segments

    # Confirm with merge edit
    if initial_count >= 2:
        segment_ids_to_merge = [skeleton.segments[0].segment_id, skeleton.segments[1].segment_id]

        edits = [
            {
                "operation": "merge",
                "segment_ids": segment_ids_to_merge
            }
        ]

        confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, edits)

        assert confirmed.status == "confirmed"
        assert confirmed.total_segments == initial_count - 1
        assert confirmed.user_edits is not None
        assert "edits" in confirmed.user_edits


def test_phase2_flow_short_narrative(temp_project_media):
    """Test Phase 2 flow with short narrative (fallback parsing)."""
    media_files = temp_project_media["all_files"]

    input_contract = ProjectInputContract(
        project_name="Short Project",
        travel_note="短游记。" * 5,
        media_files=media_files
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    # Parse story (should use fallback)
    skeleton = StoryParser.parse_story(project_id, config.travel_note)

    assert skeleton is not None
    assert skeleton.total_segments >= 3
    assert skeleton.status == "draft"

    # Confirm skeleton
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    assert confirmed.status == "confirmed"
    assert confirmed.total_segments >= 3


def test_phase2_flow_multiple_confirmations(temp_project_media):
    """Test Phase 2 flow with multiple confirmation attempts."""
    media_files = temp_project_media["all_files"]

    input_contract = ProjectInputContract(
        project_name="Multi-confirm Project",
        travel_note="这是第一段。" * 15 + "这是第二段。" * 15 + "这是第三段。" * 15 + "这是第四段。" * 15,
        media_files=media_files
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    # Parse story
    skeleton = StoryParser.parse_story(project_id, config.travel_note)

    # First confirmation
    confirmed1 = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])
    assert confirmed1.status == "confirmed"

    # Retrieve and verify
    current = StorySkeleton.get_current_skeleton(project_id)
    assert current.status == "confirmed"
    assert current.skeleton_id == skeleton.skeleton_id
