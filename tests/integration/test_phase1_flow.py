"""Integration tests for Phase 1 flow."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.input_validator import InputValidator
from src.server.modules.asset_indexer import AssetIndexer


@pytest.fixture
def temp_project_media():
    """Create temporary project with media files."""
    temp_dir = tempfile.mkdtemp()

    # Create video files
    video_files = []
    for i in range(5):
        video_path = os.path.join(temp_dir, f"video_{i}.mp4")
        Path(video_path).write_bytes(b"dummy video content")
        video_files.append(video_path)

    # Create photo files
    photo_files = []
    for i in range(50):
        photo_path = os.path.join(temp_dir, f"photo_{i}.jpg")
        Path(photo_path).write_bytes(b"dummy photo content")
        photo_files.append(photo_path)

    yield {
        "temp_dir": temp_dir,
        "videos": video_files,
        "photos": photo_files,
        "all_files": video_files + photo_files
    }

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_complete_phase1_flow(temp_project_media):
    """Test complete Phase 1 flow: create project, validate, index assets."""
    media_files = temp_project_media["all_files"]

    # Step 1: Create project
    input_contract = ProjectInputContract(
        project_name="Travel Vlog Project",
        travel_note="This is a comprehensive travel narrative describing an amazing journey. " * 20,
        media_files=media_files,
        bgm_asset="bgm.mp3",
        tts_voice="female"
    )

    project_id = ProjectManager.create_project(input_contract)
    assert project_id is not None

    # Step 2: Validate input
    validation_report = InputValidator.validate(project_id, input_contract)
    assert validation_report.project_id == project_id
    # Note: Dummy files don't have real video duration, so validation may fail on duration check
    # This test validates the structure and media counting
    assert validation_report.media_summary['total_videos'] == 5
    assert validation_report.media_summary['total_photos'] == 50

    # Step 3: Index assets
    asset_index = AssetIndexer.index_assets(project_id, media_files)
    assert asset_index.project_id == project_id
    assert asset_index.total_videos == 5
    assert asset_index.total_photos == 50
    assert len(asset_index.media_items) == 55

    # Step 4: Update project status
    ProjectManager.update_project_status(project_id, "ready")
    metadata = ProjectManager.get_project_metadata(project_id)
    assert metadata.status == "ready"

    # Step 5: Verify all data is persisted
    config = ProjectManager.get_project_config(project_id)
    assert config.travel_note == input_contract.travel_note
    assert config.bgm_asset == "bgm.mp3"
    assert config.tts_voice == "female"


def test_phase1_flow_with_insufficient_media(temp_project_media):
    """Test Phase 1 flow with insufficient media."""
    # Use only 2 videos and 20 photos (below recommended minimums)
    media_files = temp_project_media["videos"][:2] + temp_project_media["photos"][:20]

    input_contract = ProjectInputContract(
        project_name="Small Project",
        travel_note="This is a travel narrative. " * 20,
        media_files=media_files
    )

    project_id = ProjectManager.create_project(input_contract)
    validation_report = InputValidator.validate(project_id, input_contract)

    # Should have warnings about insufficient media
    assert len(validation_report.warnings) > 0
    assert validation_report.media_summary['total_videos'] == 2
    assert validation_report.media_summary['total_photos'] == 20


def test_phase1_flow_with_invalid_input():
    """Test Phase 1 flow with invalid input."""
    input_contract = ProjectInputContract(
        project_name="Invalid Project",
        travel_note="Short",  # Too short
        media_files=[]  # No media
    )

    project_id = ProjectManager.create_project(input_contract)
    validation_report = InputValidator.validate(project_id, input_contract)

    # Should be invalid
    assert validation_report.is_valid is False
    assert len(validation_report.errors) > 0
