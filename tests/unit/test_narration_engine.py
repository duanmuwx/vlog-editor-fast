"""Unit tests for NarrationEngine."""

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
from src.server.modules.narration_engine import NarrationEngine
from tests.unit.conftest import create_test_project_with_highlights


@pytest.fixture
def temp_project_with_timeline():
    """Create temporary project with timeline."""
    project_id, skeleton_id, confirmed, temp_dir = create_test_project_with_highlights(
        "Narration Engine Test",
        "这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15
    )

    timeline = EditPlanner.plan_edit(project_id)

    yield project_id, timeline.timeline_id, "default", temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_generate_narration_complete(temp_project_with_timeline):
    """Test complete narration generation."""
    project_id, timeline_id, tts_voice, _ = temp_project_with_timeline

    narration = NarrationEngine.generate_narration(project_id, timeline_id, tts_voice)

    assert narration.narration_id is not None
    assert narration.project_id == project_id
    assert len(narration.narration_text) > 0
    assert len(narration.subtitles) > 0
    assert len(narration.text_cards) > 0


def test_narration_text_generated(temp_project_with_timeline):
    """Test narration text is generated."""
    project_id, timeline_id, tts_voice, _ = temp_project_with_timeline

    narration = NarrationEngine.generate_narration(project_id, timeline_id, tts_voice)

    assert len(narration.narration_text) > 0
    assert "故事" in narration.narration_text or len(narration.narration_text) > 10


def test_subtitles_generated(temp_project_with_timeline):
    """Test subtitles are generated."""
    project_id, timeline_id, tts_voice, _ = temp_project_with_timeline

    narration = NarrationEngine.generate_narration(project_id, timeline_id, tts_voice)

    assert len(narration.subtitles) > 0
    for subtitle in narration.subtitles:
        assert subtitle.subtitle_id is not None
        assert len(subtitle.text) > 0
        assert subtitle.start_time >= 0
        assert subtitle.end_time > subtitle.start_time


def test_text_cards_generated(temp_project_with_timeline):
    """Test text cards are generated."""
    project_id, timeline_id, tts_voice, _ = temp_project_with_timeline

    narration = NarrationEngine.generate_narration(project_id, timeline_id, tts_voice)

    assert len(narration.text_cards) > 0
    for text_card in narration.text_cards:
        assert text_card.card_id is not None
        assert len(text_card.text) > 0
        assert text_card.duration_seconds > 0
        assert text_card.position in ["center", "top", "bottom"]


def test_tts_audio_path_created(temp_project_with_timeline):
    """Test TTS audio file is created."""
    project_id, timeline_id, tts_voice, _ = temp_project_with_timeline

    narration = NarrationEngine.generate_narration(project_id, timeline_id, tts_voice)

    assert narration.tts_audio_path is not None
    assert os.path.exists(narration.tts_audio_path)
