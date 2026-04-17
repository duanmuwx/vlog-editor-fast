"""Unit tests for MediaAnalyzer."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.media_analyzer import MediaAnalyzer


@pytest.fixture
def temp_project_with_media():
    """Create temporary project with test media files."""
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

    input_contract = ProjectInputContract(
        project_name="Media Analyzer Test",
        travel_note="测试游记。" * 50,
        media_files=video_files + photo_files,
    )

    project_id = ProjectManager.create_project(input_contract)

    yield project_id, temp_dir

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_analyze_media_complete(temp_project_with_media):
    """Test complete media analysis."""
    project_id, _ = temp_project_with_media

    analysis = MediaAnalyzer.analyze_media(project_id)

    assert analysis.analysis_id is not None
    assert analysis.project_id == project_id
    assert analysis.total_shots >= 0
    assert analysis.analysis_status in ["completed", "partial", "degraded"]


def test_score_quality_heuristic():
    """Test quality scoring heuristic."""
    import numpy as np

    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

    score = MediaAnalyzer._score_quality_heuristic(frame)

    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_extract_visual_features():
    """Test visual feature extraction."""
    import numpy as np

    frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

    features = MediaAnalyzer._extract_visual_features(frame)

    assert isinstance(features, dict)
    assert "brightness" in features
    assert "edge_density" in features
    assert "dominant_color" in features
    assert "scene_type" in features
    assert 0.0 <= features["brightness"] <= 1.0
    assert 0.0 <= features["edge_density"] <= 1.0


def test_compute_frame_difference():
    """Test frame difference computation."""
    import numpy as np

    frame1 = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    frame2 = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

    diff = MediaAnalyzer._compute_frame_difference(frame1, frame2)

    assert isinstance(diff, float)
    assert diff >= 0.0


def test_compute_histogram_difference():
    """Test histogram difference computation."""
    import numpy as np
    import cv2

    frame1 = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    frame2 = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

    hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
    hist1 = cv2.calcHist([hsv1], [0, 1], None, [180, 256], [0, 180, 0, 256])

    diff = MediaAnalyzer._compute_histogram_difference(hist1, frame2)

    assert isinstance(diff, float)
    assert diff >= 0.0

