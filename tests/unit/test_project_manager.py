"""Unit tests for ProjectManager."""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_create_project():
    """Test project creation."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="This is a test travel note with enough content to pass validation.",
        media_files=[],
        bgm_asset=None,
        tts_voice=None
    )

    project_id = ProjectManager.create_project(input_contract)

    assert project_id is not None
    assert len(project_id) > 0


def test_get_project_config():
    """Test getting project config."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="This is a test travel note with enough content to pass validation.",
        media_files=[],
        bgm_asset="bgm.mp3",
        tts_voice="female"
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    assert config is not None
    assert config.travel_note == input_contract.travel_note
    assert config.bgm_asset == "bgm.mp3"
    assert config.tts_voice == "female"


def test_get_project_metadata():
    """Test getting project metadata."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="This is a test travel note with enough content to pass validation.",
        media_files=[]
    )

    project_id = ProjectManager.create_project(input_contract)
    metadata = ProjectManager.get_project_metadata(project_id)

    assert metadata is not None
    assert metadata.project_name == "Test Project"
    assert metadata.status == "draft"


def test_update_project_status():
    """Test updating project status."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="This is a test travel note with enough content to pass validation.",
        media_files=[]
    )

    project_id = ProjectManager.create_project(input_contract)
    ProjectManager.update_project_status(project_id, "ready")

    metadata = ProjectManager.get_project_metadata(project_id)
    assert metadata.status == "ready"
