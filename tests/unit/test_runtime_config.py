"""Unit tests for Phase 8 runtime configuration and output paths."""

from pathlib import Path

from src.server.config import get_settings
from src.server.modules.audio_composer import AudioComposer
from src.server.modules.edit_planner import EditPlanner
from src.server.modules.narration_engine import NarrationEngine
from src.server.modules.renderer import Renderer
from src.server.storage.database import get_app_logs_dir, get_project_subdir
from tests.unit.conftest import create_test_project_with_highlights


def test_runtime_settings_read_from_environment(tmp_path, monkeypatch):
    """Runtime settings resolve Phase 8 environment variables."""
    app_data_dir = tmp_path / ".vlog-editor"
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_DATA_DIR", str(app_data_dir))
    monkeypatch.setenv("SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("SERVER_PORT", "8100")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.app_env == "production"
    assert settings.app_data_dir == app_data_dir
    assert settings.app_logs_dir == app_data_dir / "logs"
    assert settings.server_host == "127.0.0.1"
    assert settings.server_port == 8100
    assert settings.log_level == "DEBUG"


def test_runtime_outputs_follow_app_data_dir(tmp_path, monkeypatch):
    """Narration, audio mix, and exports use APP_DATA_DIR project subdirectories."""
    app_data_dir = tmp_path / ".vlog-editor"
    monkeypatch.setenv("APP_DATA_DIR", str(app_data_dir))
    get_settings.cache_clear()

    project_id, _, _, temp_dir = create_test_project_with_highlights(
        "Phase 8 Runtime Paths",
        "这是第一段故事。" * 15 + "这是第二段故事。" * 15 + "这是第三段故事。" * 15,
    )

    try:
        timeline = EditPlanner.plan_edit(project_id)
        narration = NarrationEngine.generate_narration(project_id, timeline.timeline_id, "default")
        audio_mix = AudioComposer.compose_audio(
            project_id, timeline.timeline_id, narration.narration_id, ""
        )
        export_bundle = Renderer.render_export(
            project_id,
            timeline.timeline_id,
            audio_mix.audio_mix_id,
            narration.narration_id,
        )

        expected_audio_dir = get_project_subdir(project_id, "audio", create=False)
        expected_export_dir = get_project_subdir(project_id, "exports", create=False)

        assert Path(narration.tts_audio_path).parent == expected_audio_dir
        assert Path(audio_mix.mixed_audio_path).parent == expected_audio_dir
        assert Path(export_bundle.video_path).parent == expected_export_dir
        assert Path(export_bundle.manifest_path).parent == expected_export_dir
        assert get_app_logs_dir(create=True) == app_data_dir / "logs"
    finally:
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
