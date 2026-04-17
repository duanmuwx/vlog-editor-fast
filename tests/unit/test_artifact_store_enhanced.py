"""Unit tests for artifact store enhancements."""

import pytest
import uuid
from datetime import datetime
from src.server.modules.artifact_store import (
    ArtifactStore, DependencyGraph, VersionReuse
)
from src.server.modules.project_manager import ProjectManager
from src.shared.types import ProjectInputContract


@pytest.fixture
def test_project():
    """Create test project."""
    input_contract = ProjectInputContract(
        project_name="Test Project",
        travel_note="Test narrative",
        media_files=[],
        bgm_asset="test.mp3",
        tts_voice="default"
    )
    return ProjectManager.create_project(input_contract)


class TestArtifactStore:
    """Test ArtifactStore functionality."""

    def test_create_version(self, test_project):
        """Test version creation."""
        version_id = ArtifactStore.create_version(
            "timeline", test_project,
            upstream_versions={"story": "v1"}
        )
        assert version_id is not None
        assert len(version_id) > 0

    def test_get_version(self, test_project):
        """Test retrieving version."""
        version_id = ArtifactStore.create_version("timeline", test_project)
        version = ArtifactStore.get_version(version_id, test_project)

        assert version is not None
        assert version.version_id == version_id
        assert version.artifact_type == "timeline"
        assert version.status == "active"

    def test_invalidate_version(self, test_project):
        """Test version invalidation."""
        version_id = ArtifactStore.create_version("timeline", test_project)
        ArtifactStore.invalidate_version(version_id, test_project)

        version = ArtifactStore.get_version(version_id, test_project)
        assert version.status == "invalidated"

    def test_get_active_version(self, test_project):
        """Test getting active version."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("timeline", test_project)

        active = ArtifactStore.get_active_version(test_project, "timeline")
        assert active.version_id == v2

    def test_rollback_version(self, test_project):
        """Test version rollback."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("timeline", test_project)

        ArtifactStore.rollback_version(test_project, "timeline", v1)

        active = ArtifactStore.get_active_version(test_project, "timeline")
        assert active.version_id == v1

    def test_mark_superseded(self, test_project):
        """Test marking version as superseded."""
        version_id = ArtifactStore.create_version("timeline", test_project)
        ArtifactStore.mark_superseded(version_id, test_project)

        version = ArtifactStore.get_version(version_id, test_project)
        assert version.status == "superseded"

    def test_get_version_history(self, test_project):
        """Test retrieving version history."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("timeline", test_project)
        v3 = ArtifactStore.create_version("timeline", test_project)

        history = ArtifactStore.get_version_history(test_project, "timeline")

        assert history is not None
        assert len(history.versions) >= 3
        assert history.active_version_id == v3

    def test_switch_to_version(self, test_project):
        """Test switching to specific version."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("timeline", test_project)

        ArtifactStore.switch_to_version(test_project, "timeline", v1)

        active = ArtifactStore.get_active_version(test_project, "timeline")
        assert active.version_id == v1

    def test_get_version_diff(self, test_project):
        """Test version comparison."""
        v1 = ArtifactStore.create_version(
            "timeline", test_project,
            upstream_versions={"story": "v1", "highlights": "v1"}
        )
        v2 = ArtifactStore.create_version(
            "timeline", test_project,
            upstream_versions={"story": "v2", "highlights": "v1", "media": "v1"}
        )

        diff = ArtifactStore.get_version_diff(test_project, v1, v2)

        assert diff is not None
        assert "upstream_changes" in diff
        assert "added" in diff["upstream_changes"]
        assert "modified" in diff["upstream_changes"]


class TestDependencyGraph:
    """Test DependencyGraph functionality."""

    def test_add_dependency(self, test_project):
        """Test adding dependency."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("narration", test_project)

        DependencyGraph.add_dependency(
            test_project, v2, v1, "timeline"
        )
        # Should not raise exception

    def test_invalidate_downstream(self, test_project):
        """Test invalidating downstream."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("narration", test_project)

        DependencyGraph.add_dependency(test_project, v2, v1, "timeline")
        invalidated = DependencyGraph.invalidate_downstream(test_project, v1)

        assert isinstance(invalidated, list)

    def test_get_affected_stages(self, test_project):
        """Test getting affected stages."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("narration", test_project)

        DependencyGraph.add_dependency(test_project, v2, v1, "timeline")
        stages = DependencyGraph.get_affected_stages(test_project, v1)

        assert "narration_generation" in stages

    def test_validate_upstream(self, test_project):
        """Test validating upstream."""
        v1 = ArtifactStore.create_version("timeline", test_project)

        assert DependencyGraph.validate_upstream(test_project, v1) is True

        ArtifactStore.invalidate_version(v1, test_project)
        assert DependencyGraph.validate_upstream(test_project, v1) is False


class TestVersionReuse:
    """Test VersionReuse functionality."""

    def test_can_reuse_version(self, test_project):
        """Test checking reusable version."""
        upstream = {"story": "v1", "highlights": "v1"}

        v1 = ArtifactStore.create_version(
            "timeline", test_project,
            upstream_versions=upstream
        )

        reusable = VersionReuse.can_reuse_version(
            test_project, "timeline", upstream
        )

        assert reusable == v1

    def test_can_reuse_version_not_found(self, test_project):
        """Test when reusable version not found."""
        upstream = {"story": "v1", "highlights": "v1"}

        reusable = VersionReuse.can_reuse_version(
            test_project, "timeline", upstream
        )

        assert reusable is None

    def test_mark_reused(self, test_project):
        """Test marking version as reused."""
        v1 = ArtifactStore.create_version("timeline", test_project)
        v2 = ArtifactStore.create_version("timeline", test_project)

        VersionReuse.mark_reused(v2, test_project, v1)
        # Should not raise exception
