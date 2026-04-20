"""Stress testing fixtures and utilities."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def stress_test_dir():
    """Create a temporary directory for stress testing."""
    temp_dir = tempfile.mkdtemp(prefix="vlog_stress_")
    yield Path(temp_dir)
    # Cleanup is handled by OS


@pytest.fixture
def concurrent_projects_setup():
    """Setup for concurrent project testing."""
    projects = []
    for i in range(5):
        project = {
            "project_id": f"project_{i}",
            "name": f"Test Project {i}",
            "media_count": 50 + i * 10,
            "narrative_length": 3000 + i * 500,
        }
        projects.append(project)
    return projects


@pytest.fixture
def resource_monitor():
    """Monitor resource usage during stress tests."""
    import psutil

    monitor = {
        "process": psutil.Process(),
        "start_memory": None,
        "peak_memory": None,
        "start_cpu": None,
        "peak_cpu": None,
    }
    return monitor
