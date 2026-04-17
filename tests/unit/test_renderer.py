"""Unit tests for Renderer."""

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
from src.server.modules.renderer import Renderer


@pytest.fixture
def temp_project_with_audio():
    """Create temporary project with audio mix."""
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
        project_name="Renderer Test",
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
    audio_mix = AudioComposer.compose_audio(project_id, timeline.timeline_id, narration.narration_id, bgm_path)

    yield project_id, timeline.timeline_id, audio_mix.audio_mix_id, narration.narration_id, temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_render_export_complete(temp_project_with_audio):
    """Test complete rendering and export."""
    project_id, timeline_id, audio_mix_id, narration_id, _ = temp_project_with_audio

    export_bundle = Renderer.render_export(project_id, timeline_id, audio_mix_id, narration_id)

    assert export_bundle.export_id is not None
    assert export_bundle.project_id == project_id
    assert export_bundle.status == "success"


def test_export_files_created(temp_project_with_audio):
    """Test export files are created."""
    project_id, timeline_id, audio_mix_id, narration_id, _ = temp_project_with_audio

    export_bundle = Renderer.render_export(project_id, timeline_id, audio_mix_id, narration_id)

    assert os.path.exists(export_bundle.video_path)
    assert os.path.exists(export_bundle.subtitle_path)
    assert os.path.exists(export_bundle.manifest_path)


def test_srt_subtitles_created(temp_project_with_audio):
    """Test SRT subtitles are created."""
    project_id, timeline_id, audio_mix_id, narration_id, _ = temp_project_with_audio

    export_bundle = Renderer.render_export(project_id, timeline_id, audio_mix_id, narration_id)

    assert export_bundle.subtitle_path is not None
    assert os.path.exists(export_bundle.subtitle_path)
    assert export_bundle.subtitle_path.endswith(".srt")

    # Check SRT format
    with open(export_bundle.subtitle_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert len(content) > 0


def test_manifest_created(temp_project_with_audio):
    """Test manifest JSON is created."""
    project_id, timeline_id, audio_mix_id, narration_id, _ = temp_project_with_audio

    export_bundle = Renderer.render_export(project_id, timeline_id, audio_mix_id, narration_id)

    assert export_bundle.manifest_path is not None
    assert os.path.exists(export_bundle.manifest_path)
    assert export_bundle.manifest_path.endswith(".json")

    # Check manifest content
    import json
    with open(export_bundle.manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        assert manifest["project_id"] == project_id
        assert manifest["video_codec"] == Renderer.VIDEO_CODEC


def test_video_path_valid(temp_project_with_audio):
    """Test video path is valid."""
    project_id, timeline_id, audio_mix_id, narration_id, _ = temp_project_with_audio

    export_bundle = Renderer.render_export(project_id, timeline_id, audio_mix_id, narration_id)

    assert export_bundle.video_path is not None
    assert export_bundle.video_path.endswith(".mp4")
    assert os.path.exists(export_bundle.video_path)
