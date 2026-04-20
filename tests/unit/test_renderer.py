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
from tests.unit.conftest import create_test_project_with_highlights


@pytest.fixture
def temp_project_with_audio():
    """Create temporary project with audio mix."""
    temp_dir = tempfile.mkdtemp()

    # Create BGM file
    bgm_path = os.path.join(temp_dir, "bgm.mp3")
    Path(bgm_path).write_bytes(b"dummy bgm")

    project_id, skeleton_id, confirmed, _ = create_test_project_with_highlights(
        "Renderer Test",
        "这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15
    )

    timeline = EditPlanner.plan_edit(project_id)
    narration = NarrationEngine.generate_narration(project_id, timeline.timeline_id, "default")
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
