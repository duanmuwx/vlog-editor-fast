"""Unit tests for AlignmentEngine."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract, StorySegment, MediaShot
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser
from src.server.modules.skeleton_confirmation import SkeletonConfirmation
from src.server.modules.media_analyzer import MediaAnalyzer
from src.server.modules.alignment_engine import AlignmentEngine


@pytest.fixture
def temp_project_with_alignment():
    """Create temporary project with story and media."""
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
        project_name="Alignment Test",
        travel_note="这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15,
        media_files=video_files + photo_files,
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    MediaAnalyzer.analyze_media(project_id)

    yield project_id, skeleton.skeleton_id, confirmed, temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_align_media_complete(temp_project_with_alignment):
    """Test complete media alignment."""
    project_id, skeleton_id, skeleton, _ = temp_project_with_alignment

    candidates = AlignmentEngine.align_media(project_id, skeleton_id)

    assert len(candidates) > 0

    for candidate in candidates:
        assert candidate.candidate_id is not None
        assert candidate.segment_id is not None
        assert candidate.shot_id is not None
        assert 0.0 <= candidate.match_score <= 1.0
        assert 0.0 <= candidate.text_match_score <= 1.0
        assert candidate.reasoning is not None


def test_score_text_match():
    """Test text-visual matching."""
    summary = "我们在北京参观了长城，看到了美丽的风景。"
    keywords = ["北京", "长城", "风景"]
    visual_features = {"dominant_color": "green", "scene_type": "outdoor"}

    score = AlignmentEngine._score_text_match(summary, keywords, visual_features)

    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_score_text_match_no_features():
    """Test text-visual matching with no features."""
    summary = "测试摘要"
    keywords = ["测试"]
    visual_features = {}

    score = AlignmentEngine._score_text_match(summary, keywords, visual_features)

    assert isinstance(score, float)
    assert score == 0.3


def test_score_time_match():
    """Test time-based matching."""
    timestamps = ["第一天", "上午10点"]
    shot_start_time = 600.0

    score = AlignmentEngine._score_time_match(timestamps, shot_start_time)

    assert score is None or (isinstance(score, float) and 0.0 <= score <= 1.0)


def test_score_time_match_no_timestamps():
    """Test time matching with no timestamps."""
    timestamps = []
    shot_start_time = 600.0

    score = AlignmentEngine._score_time_match(timestamps, shot_start_time)

    assert score is None


def test_score_location_match():
    """Test location-based matching."""
    locations = ["北京", "长城"]

    score_photo = AlignmentEngine._score_location_match(locations, "photo")
    assert score_photo == 0.6

    score_video = AlignmentEngine._score_location_match(locations, "video_shot")
    assert score_video == 0.3


def test_score_location_match_no_locations():
    """Test location matching with no locations."""
    locations = []

    score = AlignmentEngine._score_location_match(locations, "photo")

    assert score is None


def test_generate_reasoning():
    """Test reasoning generation."""
    segment = StorySegment(
        segment_id="seg1",
        title="第一段",
        summary="我们在北京参观了长城",
        start_index=0,
        end_index=100,
        importance="high",
        confidence=0.9,
        keywords=["北京", "长城"],
        locations=["北京"],
        timestamps=["第一天"],
    )

    shot = MediaShot(
        shot_id="shot1",
        file_id="file1",
        shot_type="photo",
        quality_score=0.8,
        has_audio=False,
        visual_features={"scene_type": "outdoor"},
        confidence=0.9,
    )

    reasoning = AlignmentEngine._generate_reasoning(segment, shot, 0.7, 0.6, 0.6)

    assert isinstance(reasoning, str)
    assert len(reasoning) > 0
