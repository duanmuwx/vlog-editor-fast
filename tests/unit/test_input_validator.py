"""Unit tests for InputValidator."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.input_validator import InputValidator
from src.server.modules.project_manager import ProjectManager


@pytest.fixture
def temp_media_files():
    """Create temporary media files."""
    temp_dir = tempfile.mkdtemp()

    # Create dummy video files
    video_files = []
    for i in range(5):
        video_path = os.path.join(temp_dir, f"video_{i}.mp4")
        Path(video_path).touch()
        video_files.append(video_path)

    # Create dummy photo files
    photo_files = []
    for i in range(50):
        photo_path = os.path.join(temp_dir, f"photo_{i}.jpg")
        Path(photo_path).touch()
        photo_files.append(photo_path)

    yield video_files + photo_files

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_check_narrative_length_valid():
    """Test narrative length check with valid input."""
    text = "This is a valid travel narrative with enough content. " * 10
    is_valid, msg = InputValidator.check_narrative_length(text)
    assert is_valid is True


def test_check_narrative_length_invalid():
    """Test narrative length check with invalid input."""
    text = "Short"
    is_valid, msg = InputValidator.check_narrative_length(text)
    assert is_valid is False


def test_check_media_files_valid(temp_media_files):
    """Test media files check with valid files."""
    is_valid, errors = InputValidator.check_media_files(temp_media_files)
    assert is_valid is True
    assert len(errors) == 0


def test_check_media_files_missing():
    """Test media files check with missing files."""
    files = ["/nonexistent/file.mp4"]
    is_valid, errors = InputValidator.check_media_files(files)
    assert is_valid is False
    assert len(errors) > 0


def test_check_media_files_unsupported_format():
    """Test media files check with unsupported format."""
    temp_dir = tempfile.mkdtemp()
    unsupported_file = os.path.join(temp_dir, "file.xyz")
    Path(unsupported_file).touch()

    is_valid, errors = InputValidator.check_media_files([unsupported_file])
    assert is_valid is False

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_analyze_media_files(temp_media_files):
    """Test media files analysis."""
    summary = InputValidator.analyze_media_files(temp_media_files)

    assert summary['total_files'] == 55
    assert summary['total_videos'] == 5
    assert summary['total_photos'] == 50


def test_validate_valid_input(temp_media_files):
    """Test complete validation with valid input."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="This is a valid travel narrative with enough content. " * 10,
        media_files=temp_media_files
    )

    project_id = ProjectManager.create_project(input_contract)
    report = InputValidator.validate(project_id, input_contract)

    # Note: Dummy files don't have real video metadata, so duration is estimated
    # This test validates the structure, not the actual duration check
    assert report.project_id == project_id
    assert report.media_summary['total_videos'] == 5
    assert report.media_summary['total_photos'] == 50


def test_validate_short_narrative():
    """Test validation with short narrative."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="Short",
        media_files=[]
    )

    project_id = ProjectManager.create_project(input_contract)
    report = InputValidator.validate(project_id, input_contract)

    assert report.is_valid is False
    assert len(report.errors) > 0


def test_analyze_metadata_coverage():
    """Test metadata coverage analysis."""
    coverage = InputValidator.analyze_metadata_coverage([])

    assert 'exif_coverage' in coverage
    assert 'gps_coverage' in coverage
    assert 'timestamp_coverage' in coverage
    assert 'audio_coverage' in coverage
