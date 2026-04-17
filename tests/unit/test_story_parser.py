"""Unit tests for StoryParser."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser


@pytest.fixture
def temp_project():
    """Create temporary project."""
    temp_dir = tempfile.mkdtemp()

    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="这是一个旅行游记。第一天我们到达了北京。" * 20,
        media_files=[]
    )

    project_id = ProjectManager.create_project(input_contract)

    yield project_id

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_parse_story_valid_narrative(temp_project):
    """Test parsing valid narrative."""
    config = ProjectManager.get_project_config(temp_project)

    skeleton = StoryParser.parse_story(temp_project, config.travel_note)

    assert skeleton is not None
    assert skeleton.project_id == temp_project
    assert 3 <= skeleton.total_segments <= 8
    assert len(skeleton.segments) == skeleton.total_segments
    assert 0 <= skeleton.narrative_coverage <= 1.0
    assert 0 <= skeleton.parsing_confidence <= 1.0
    assert skeleton.status == "draft"


def test_parse_story_short_narrative(temp_project):
    """Test parsing short narrative with fallback."""
    short_narrative = "短游记"

    skeleton = StoryParser.parse_story(temp_project, short_narrative)

    assert skeleton is not None
    assert skeleton.total_segments >= 3


def test_parse_story_segment_count_validation(temp_project):
    """Test that segment count is within valid range."""
    config = ProjectManager.get_project_config(temp_project)

    skeleton = StoryParser.parse_story(temp_project, config.travel_note)

    assert StoryParser.MIN_SEGMENTS <= skeleton.total_segments <= StoryParser.MAX_SEGMENTS


def test_parse_story_segments_have_required_fields(temp_project):
    """Test that all segments have required fields."""
    config = ProjectManager.get_project_config(temp_project)

    skeleton = StoryParser.parse_story(temp_project, config.travel_note)

    for segment in skeleton.segments:
        assert segment.segment_id
        assert segment.title
        assert segment.summary
        assert segment.importance in ["high", "medium", "low"]
        assert 0 <= segment.confidence <= 1.0
        assert isinstance(segment.keywords, list)
        assert isinstance(segment.locations, list)
        assert isinstance(segment.timestamps, list)


def test_fallback_parse_generates_segments():
    """Test fallback parsing generates valid segments."""
    narrative = "这是第一段。这是第二段。这是第三段。" * 10

    segments = StoryParser._fallback_parse(narrative)

    assert len(segments) >= StoryParser.MIN_SEGMENTS
    assert len(segments) <= StoryParser.MAX_SEGMENTS
    assert all(seg.segment_id for seg in segments)
    assert all(seg.title for seg in segments)
