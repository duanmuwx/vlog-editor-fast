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


@pytest.fixture
def temp_project_with_narration():
    """Create temporary project with narration."""
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

    # Create BGM file
    bgm_path = os.path.join(temp_dir, "bgm.mp3")
    Path(bgm_path).write_bytes(b"dummy bgm")

    input_contract = ProjectInputContract(
        project_name="Audio Composer Test",
        travel_note="这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15,
        media_files=video_files + photo_files,
        bgm_asset=bgm_path,
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
    narration = NarrationEngine.generate_narration(project_id, timeline.timeline_id, config.tts_voice)

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
