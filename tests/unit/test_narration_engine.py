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


@pytest.fixture
def temp_project_with_timeline():
    """Create temporary project with timeline."""
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
        project_name="Narration Engine Test",
        travel_note="这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15,
        media_files=video_files + photo_files,
        tts_voice="default"
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

    timeline = EditPlanner.plan_edit(project_id)

    yield project_id, timeline.timeline_id, config.tts_voice, temp_dir

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
