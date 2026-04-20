"""Unit tests for AudioComposer."""

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
from src.server.modules.audio_composer import AudioComposer
from tests.unit.conftest import create_test_project_with_highlights


@pytest.fixture
def temp_project_with_narration():
    """Create temporary project with narration."""
    temp_dir = tempfile.mkdtemp()

    # Create BGM file
    bgm_path = os.path.join(temp_dir, "bgm.mp3")
    Path(bgm_path).write_bytes(b"dummy bgm")

    project_id, skeleton_id, confirmed, _ = create_test_project_with_highlights(
        "Audio Composer Test",
        "这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15
    )

    timeline = EditPlanner.plan_edit(project_id)
    narration = NarrationEngine.generate_narration(project_id, timeline.timeline_id, "default")

    yield project_id, timeline.timeline_id, narration.narration_id, bgm_path, temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_compose_audio_complete(temp_project_with_narration):
    """Test complete audio composition."""
    project_id, timeline_id, narration_id, bgm_path, _ = temp_project_with_narration

    audio_mix = AudioComposer.compose_audio(project_id, timeline_id, narration_id, bgm_path)

    assert audio_mix.audio_mix_id is not None
    assert audio_mix.project_id == project_id
    assert audio_mix.total_duration_seconds > 0
    assert len(audio_mix.tracks) > 0


def test_audio_tracks_created(temp_project_with_narration):
    """Test audio tracks are created."""
    project_id, timeline_id, narration_id, bgm_path, _ = temp_project_with_narration

    audio_mix = AudioComposer.compose_audio(project_id, timeline_id, narration_id, bgm_path)

    # Should have narration, ambient, and BGM tracks
    track_types = [track.track_type for track in audio_mix.tracks]
    assert "narration" in track_types


def test_narration_track_volume(temp_project_with_narration):
    """Test narration track has correct volume."""
    project_id, timeline_id, narration_id, bgm_path, _ = temp_project_with_narration

    audio_mix = AudioComposer.compose_audio(project_id, timeline_id, narration_id, bgm_path)

    narration_track = next(
        (t for t in audio_mix.tracks if t.track_type == "narration"),
        None
    )

    assert narration_track is not None
    assert narration_track.volume == AudioComposer.NARRATION_VOLUME


def test_mixed_audio_file_created(temp_project_with_narration):
    """Test mixed audio file is created."""
    project_id, timeline_id, narration_id, bgm_path, _ = temp_project_with_narration

    audio_mix = AudioComposer.compose_audio(project_id, timeline_id, narration_id, bgm_path)

    assert audio_mix.mixed_audio_path is not None
    assert os.path.exists(audio_mix.mixed_audio_path)


def test_audio_duration_matches_timeline(temp_project_with_narration):
    """Test audio duration matches timeline duration."""
    project_id, timeline_id, narration_id, bgm_path, _ = temp_project_with_narration

    from src.server.storage.database import get_or_create_db
    from src.server.storage.schemas import TimelineRecord

    db = get_or_create_db(project_id)
    session = db.get_session()

    try:
        timeline_record = session.query(TimelineRecord).filter_by(
            timeline_id=timeline_id
        ).first()

        audio_mix = AudioComposer.compose_audio(project_id, timeline_id, narration_id, bgm_path)

        assert audio_mix.total_duration_seconds == timeline_record.total_duration_seconds
    finally:
        session.close()
