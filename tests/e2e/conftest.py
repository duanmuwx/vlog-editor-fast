"""End-to-end testing fixtures and utilities."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def e2e_project_setup():
    """Setup a complete project for E2E testing."""
    temp_dir = tempfile.mkdtemp(prefix="vlog_e2e_")
    project_dir = Path(temp_dir) / "e2e_project"
    project_dir.mkdir(parents=True)

    # Create media directory
    media_dir = project_dir / "media"
    media_dir.mkdir()

    # Create sample videos
    for i in range(10):
        video_file = media_dir / f"video_{i:02d}.mp4"
        with open(video_file, "wb") as f:
            f.write(b"dummy_video" * 100)

    # Create sample images
    for i in range(50):
        image_file = media_dir / f"photo_{i:03d}.jpg"
        with open(image_file, "wb") as f:
            f.write(b"dummy_image" * 50)

    # Create narrative
    narrative_file = project_dir / "narrative.txt"
    narrative = """
    Day 1: 我们从北京出发，飞往巴黎。这是一次梦幻般的旅程。
    在飞机上，我们欣赏了美丽的云景。

    Day 2: 在巴黎的第一天，我们参观了埃菲尔铁塔。这座标志性建筑令人印象深刻。
    我们在塔下拍了很多照片，享受了美妙的景色。

    Day 3: 今天我们去了卢浮宫。这个世界著名的博物馆收藏了无数艺术珍品。
    我们花了整个下午欣赏蒙娜丽莎和其他杰作。

    Day 4: 我们乘坐塞纳河游船，欣赏了巴黎的美丽夜景。
    河两岸的建筑在灯光下显得格外迷人。

    Day 5: 前往凡尔赛宫。这座皇家宫殿的规模和奢华令人惊叹。
    我们在花园里漫步，拍摄了许多美丽的照片。
    """

    with open(narrative_file, "w", encoding="utf-8") as f:
        f.write(narrative)

    # Create project config
    config = {
        "project_id": "e2e_test_project",
        "name": "E2E Test Project",
        "media_dir": str(media_dir),
        "narrative_file": str(narrative_file),
        "bgm_asset": "default_bgm.mp3",
        "tts_voice": "default_voice",
    }

    config_file = project_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    yield {
        "project_dir": project_dir,
        "media_dir": media_dir,
        "narrative_file": narrative_file,
        "config_file": config_file,
        "config": config,
    }

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def e2e_state_tracker():
    """Track state changes during E2E tests."""
    state = {
        "project_created": False,
        "input_validated": False,
        "assets_indexed": False,
        "story_parsed": False,
        "skeleton_confirmed": False,
        "media_analyzed": False,
        "alignment_completed": False,
        "highlights_confirmed": False,
        "timeline_generated": False,
        "narration_generated": False,
        "audio_mixed": False,
        "video_rendered": False,
        "export_completed": False,
        "errors": [],
        "warnings": [],
    }
    return state


@pytest.fixture
def e2e_user_decisions():
    """Simulate user decisions during E2E tests."""
    decisions = {
        "skeleton_edits": [
            {"action": "merge", "segments": [0, 1]},
            {"action": "reorder", "order": [1, 0, 2, 3, 4]},
        ],
        "highlight_selections": [
            {"segment_id": 0, "shot_id": 0, "confirmed": True},
            {"segment_id": 1, "shot_id": 5, "confirmed": True},
            {"segment_id": 2, "shot_id": 10, "confirmed": True},
        ],
        "regeneration_type": "narration_only",
    }
    return decisions
