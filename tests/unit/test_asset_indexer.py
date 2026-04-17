"""Unit tests for AssetIndexer."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract, FileType
from src.server.modules.asset_indexer import AssetIndexer
from src.server.modules.project_manager import ProjectManager


@pytest.fixture
def temp_media_files():
    """Create temporary media files."""
    temp_dir = tempfile.mkdtemp()

    # Create dummy video files
    video_files = []
    for i in range(3):
        video_path = os.path.join(temp_dir, f"video_{i}.mp4")
        Path(video_path).write_bytes(b"dummy video content")
        video_files.append(video_path)

    # Create dummy photo files
    photo_files = []
    for i in range(10):
        photo_path = os.path.join(temp_dir, f"photo_{i}.jpg")
        Path(photo_path).write_bytes(b"dummy photo content")
        photo_files.append(photo_path)

    yield video_files + photo_files

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_determine_file_type():
    """Test file type determination."""
    assert AssetIndexer._determine_file_type(".mp4") == FileType.VIDEO
    assert AssetIndexer._determine_file_type(".mov") == FileType.VIDEO
    assert AssetIndexer._determine_file_type(".jpg") == FileType.PHOTO
    assert AssetIndexer._determine_file_type(".png") == FileType.PHOTO
    assert AssetIndexer._determine_file_type(".xyz") is None


def test_extract_video_metadata():
    """Test video metadata extraction."""
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "test.mp4")
    Path(video_path).write_bytes(b"dummy video")

    metadata = AssetIndexer.extract_video_metadata(video_path)

    assert metadata.file_path == video_path
    assert metadata.file_type == FileType.VIDEO
    assert metadata.file_size > 0
    assert metadata.creation_time is not None

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_extract_photo_metadata():
    """Test photo metadata extraction."""
    temp_dir = tempfile.mkdtemp()
    photo_path = os.path.join(temp_dir, "test.jpg")
    Path(photo_path).write_bytes(b"dummy photo")

    metadata = AssetIndexer.extract_photo_metadata(photo_path)

    assert metadata.file_path == photo_path
    assert metadata.file_type == FileType.PHOTO
    assert metadata.file_size > 0
    assert metadata.creation_time is not None
    assert metadata.has_audio is False

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_index_assets(temp_media_files):
    """Test asset indexing."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="This is a test travel note with enough content to pass validation.",
        media_files=temp_media_files
    )

    project_id = ProjectManager.create_project(input_contract)
    asset_index = AssetIndexer.index_assets(project_id, temp_media_files)

    assert asset_index.project_id == project_id
    assert asset_index.total_videos == 3
    assert asset_index.total_photos == 10
    assert len(asset_index.media_items) == 13
    assert asset_index.indexed_at is not None


def test_index_assets_empty():
    """Test asset indexing with empty file list."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="This is a test travel note with enough content to pass validation.",
        media_files=[]
    )

    project_id = ProjectManager.create_project(input_contract)
    asset_index = AssetIndexer.index_assets(project_id, [])

    assert asset_index.total_videos == 0
    assert asset_index.total_photos == 0
    assert len(asset_index.media_items) == 0
