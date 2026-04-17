"""Unit tests for ArtifactStore."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.artifact_store import ArtifactStore


@pytest.fixture
def temp_project():
    """Create temporary project."""
    temp_dir = tempfile.mkdtemp()

    input_contract = ProjectInputContract(
        project_name="Artifact Store Test",
        travel_note="测试游记。" * 50,
        media_files=[],
    )

    project_id = ProjectManager.create_project(input_contract)

    yield project_id, temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_create_version(temp_project):
    """Test creating artifact version."""
    project_id, _ = temp_project

    version_id = ArtifactStore.create_version(
        "timeline",
        project_id,
        upstream_versions={"skeleton": "confirmed"}
    )

    assert version_id is not None
    assert len(version_id) > 0


def test_get_version(temp_project):
    """Test retrieving artifact version."""
    project_id, _ = temp_project

    version_id = ArtifactStore.create_version(
        "timeline",
        project_id,
        upstream_versions={"skeleton": "confirmed"}
    )

    version = ArtifactStore.get_version(version_id, project_id)

    assert version is not None
    assert version.version_id == version_id
    assert version.artifact_type == "timeline"
    assert version.status == "active"


def test_get_active_version(temp_project):
    """Test getting active version."""
    project_id, _ = temp_project

    version_id = ArtifactStore.create_version(
        "timeline",
        project_id,
        upstream_versions={"skeleton": "confirmed"}
    )

    active_version = ArtifactStore.get_active_version(project_id, "timeline")

    assert active_version is not None
    assert active_version.version_id == version_id
    assert active_version.status == "active"


def test_invalidate_version(temp_project):
    """Test invalidating version."""
    project_id, _ = temp_project

    version_id = ArtifactStore.create_version(
        "timeline",
        project_id,
        upstream_versions={"skeleton": "confirmed"}
    )

    ArtifactStore.invalidate_version(version_id, project_id)

    version = ArtifactStore.get_version(version_id, project_id)

    assert version.status == "invalidated"


def test_mark_superseded(temp_project):
    """Test marking version as superseded."""
    project_id, _ = temp_project

    version_id = ArtifactStore.create_version(
        "timeline",
        project_id,
        upstream_versions={"skeleton": "confirmed"}
    )

    ArtifactStore.mark_superseded(version_id, project_id)

    version = ArtifactStore.get_version(version_id, project_id)

    assert version.status == "superseded"


def test_rollback_version(temp_project):
    """Test rolling back to previous version."""
    project_id, _ = temp_project

    # Create first version
    version_id_1 = ArtifactStore.create_version(
        "timeline",
        project_id,
        upstream_versions={"skeleton": "confirmed"}
    )

    # Create second version
    version_id_2 = ArtifactStore.create_version(
        "timeline",
        project_id,
        upstream_versions={"skeleton": "confirmed"}
    )

    # Rollback to first version
    ArtifactStore.rollback_version(project_id, "timeline", version_id_1)

    active_version = ArtifactStore.get_active_version(project_id, "timeline")

    assert active_version.version_id == version_id_1
    assert active_version.status == "active"
