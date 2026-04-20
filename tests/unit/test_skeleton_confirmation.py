"""Unit tests for SkeletonConfirmation."""

import pytest
import tempfile
from datetime import datetime

from src.shared.types import ProjectInputContract, StorySegment
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser
from src.server.modules.story_skeleton import StorySkeletonManager
from src.server.modules.skeleton_confirmation import SkeletonConfirmation


@pytest.fixture
def temp_project_with_skeleton():
    """Create temporary project with parsed skeleton."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="这是第一段故事。" * 10 + "这是第二段故事。" * 10 + "这是第三段故事。" * 10 + "这是第四段故事。" * 10,
        media_files=[]
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)

    yield project_id, skeleton

    import shutil
    shutil.rmtree(tempfile.gettempdir(), ignore_errors=True)


def test_confirm_skeleton_no_edits(temp_project_with_skeleton):
    """Test confirming skeleton without edits."""
    project_id, skeleton = temp_project_with_skeleton

    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    assert confirmed.status == "confirmed"
    assert confirmed.confirmed_at is not None
    assert confirmed.total_segments == skeleton.total_segments
    assert len(confirmed.segments) == skeleton.total_segments


def test_confirm_skeleton_with_merge(temp_project_with_skeleton):
    """Test confirming skeleton with merge operation."""
    project_id, skeleton = temp_project_with_skeleton

    if len(skeleton.segments) < 2:
        pytest.skip("Need at least 2 segments to test merge")

    segment_ids_to_merge = [skeleton.segments[0].segment_id, skeleton.segments[1].segment_id]

    edits = [
        {
            "operation": "merge",
            "segment_ids": segment_ids_to_merge
        }
    ]

    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, edits)

    assert confirmed.status == "confirmed"
    assert confirmed.total_segments == skeleton.total_segments - 1


def test_confirm_skeleton_with_delete(temp_project_with_skeleton):
    """Test confirming skeleton with delete operation."""
    project_id, skeleton = temp_project_with_skeleton

    if len(skeleton.segments) <= 3:
        pytest.skip("Need more than 3 segments to test delete")

    segment_id_to_delete = skeleton.segments[-1].segment_id

    edits = [
        {
            "operation": "delete",
            "segment_ids": [segment_id_to_delete]
        }
    ]

    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, edits)

    assert confirmed.status == "confirmed"
    assert confirmed.total_segments == skeleton.total_segments - 1
    assert all(seg.segment_id != segment_id_to_delete for seg in confirmed.segments)


def test_confirm_skeleton_with_reorder(temp_project_with_skeleton):
    """Test confirming skeleton with reorder operation."""
    project_id, skeleton = temp_project_with_skeleton

    if len(skeleton.segments) < 2:
        pytest.skip("Need at least 2 segments to test reorder")

    new_order = [seg.segment_id for seg in reversed(skeleton.segments)]

    edits = [
        {
            "operation": "reorder",
            "segment_ids": new_order
        }
    ]

    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, edits)

    assert confirmed.status == "confirmed"
    assert confirmed.total_segments == skeleton.total_segments
    assert [seg.segment_id for seg in confirmed.segments] == new_order


def test_confirm_skeleton_invalid_operation(temp_project_with_skeleton):
    """Test confirming skeleton with invalid operation."""
    project_id, skeleton = temp_project_with_skeleton

    edits = [
        {
            "operation": "invalid_op",
            "segment_ids": []
        }
    ]

    with pytest.raises(ValueError):
        SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, edits)


def test_confirm_skeleton_invalid_segment_ids(temp_project_with_skeleton):
    """Test confirming skeleton with invalid segment IDs."""
    project_id, skeleton = temp_project_with_skeleton

    edits = [
        {
            "operation": "delete",
            "segment_ids": ["invalid_segment_id"]
        }
    ]

    with pytest.raises(ValueError):
        SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, edits)


def test_confirm_skeleton_too_few_segments(temp_project_with_skeleton):
    """Test that confirming skeleton cannot result in too few segments."""
    project_id, skeleton = temp_project_with_skeleton

    if len(skeleton.segments) <= 3:
        pytest.skip("Need more than 3 segments to test minimum constraint")

    segment_ids_to_delete = [seg.segment_id for seg in skeleton.segments[3:]]

    edits = [
        {
            "operation": "delete",
            "segment_ids": segment_ids_to_delete
        }
    ]

    with pytest.raises(ValueError):
        SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, edits)


def test_confirm_skeleton_persists_to_db(temp_project_with_skeleton):
    """Test that confirmed skeleton is persisted to database."""
    project_id, skeleton = temp_project_with_skeleton

    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    retrieved = StorySkeleton.get_skeleton(project_id, skeleton.skeleton_id)

    assert retrieved is not None
    assert retrieved.status == "confirmed"
    assert retrieved.confirmed_at is not None
    assert retrieved.total_segments == confirmed.total_segments
