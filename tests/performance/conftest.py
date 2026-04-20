"""Performance testing fixtures and utilities."""

import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, List

import pytest


@pytest.fixture
def performance_metrics():
    """Collect performance metrics during test execution."""
    metrics = {
        "start_time": None,
        "end_time": None,
        "duration": None,
        "memory_peak": None,
        "memory_avg": None,
        "disk_usage": None,
    }
    return metrics


@pytest.fixture
def standard_project_dir():
    """Create a standard test project directory with typical media files."""
    temp_dir = tempfile.mkdtemp(prefix="vlog_test_")

    # Create project structure
    project_dir = Path(temp_dir) / "standard_project"
    project_dir.mkdir(parents=True)

    media_dir = project_dir / "media"
    media_dir.mkdir()

    # Create dummy video files (30 videos, ~3 min each)
    for i in range(30):
        video_file = media_dir / f"video_{i:03d}.mp4"
        # Create a minimal MP4 file (just for testing, not a real video)
        with open(video_file, "wb") as f:
            f.write(b"dummy_video_content" * 1000)  # ~19KB each

    # Create dummy image files (400 images)
    for i in range(400):
        image_file = media_dir / f"photo_{i:04d}.jpg"
        with open(image_file, "wb") as f:
            f.write(b"dummy_image_content" * 100)  # ~1.9KB each

    # Create travel narrative
    narrative_file = project_dir / "narrative.txt"
    narrative_text = """
    Day 1: 我们从北京出发，飞往巴黎。这是一次梦幻般的旅程。
    在飞机上，我们欣赏了美丽的云景。空乘人员非常友好，为我们提供了舒适的服务。
    我们在飞机上看了两部电影，享受了美味的飞行餐。

    Day 2: 在巴黎的第一天，我们参观了埃菲尔铁塔。这座标志性建筑令人印象深刻。
    我们在塔下拍了很多照片，享受了美妙的景色。塔顶的景观令人叹为观止。
    我们还在塔下的餐厅享用了法国大餐。

    Day 3: 今天我们去了卢浮宫。这个世界著名的博物馆收藏了无数艺术珍品。
    我们花了整个下午欣赏蒙娜丽莎和其他杰作。博物馆的建筑本身就是一件艺术品。
    我们还参观了古埃及文物展厅，对古代文明有了更深的了解。

    Day 4: 我们乘坐塞纳河游船，欣赏了巴黎的美丽夜景。
    河两岸的建筑在灯光下显得格外迷人。我们看到了许多著名的桥梁和建筑。
    游船上的导游为我们讲解了巴黎的历史和文化。

    Day 5: 前往凡尔赛宫。这座皇家宫殿的规模和奢华令人惊叹。
    我们在花园里漫步，拍摄了许多美丽的照片。宫殿内部的装饰令人目不转睛。
    我们还参观了国王的卧室和皇后的房间。

    Day 6: 在蒙马特区漫步，参观了圣心大教堂。
    这个地区充满了艺术气息和浪漫的氛围。我们看到了许多街头艺术家在创作。
    我们还在当地的小咖啡馆里享受了传统的法国咖啡和甜点。

    Day 7: 最后一天，我们在左岸的咖啡馆里放松。
    这次巴黎之旅给我们留下了永恒的回忆。我们拍摄了数百张照片。
    我们计划下次再来巴黎，探索更多的景点和文化。
    """ * 5  # Repeat to reach ~5000+ words

    with open(narrative_file, "w", encoding="utf-8") as f:
        f.write(narrative_text)

    yield project_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def large_project_dir():
    """Create a large test project for stress testing."""
    temp_dir = tempfile.mkdtemp(prefix="vlog_large_")

    project_dir = Path(temp_dir) / "large_project"
    project_dir.mkdir(parents=True)

    media_dir = project_dir / "media"
    media_dir.mkdir()

    # Create 100 video files
    for i in range(100):
        video_file = media_dir / f"video_{i:04d}.mp4"
        with open(video_file, "wb") as f:
            f.write(b"dummy_video_content" * 2000)  # ~38KB each

    # Create 1000 image files
    for i in range(1000):
        image_file = media_dir / f"photo_{i:05d}.jpg"
        with open(image_file, "wb") as f:
            f.write(b"dummy_image_content" * 100)  # ~1.9KB each

    # Create long narrative (10000+ words)
    narrative_file = project_dir / "narrative.txt"
    base_narrative = """
    Day 1: 我们从北京出发，飞往巴黎。这是一次梦幻般的旅程。
    在飞机上，我们欣赏了美丽的云景。空乘人员非常友好，为我们提供了舒适的服务。

    Day 2: 在巴黎的第一天，我们参观了埃菲尔铁塔。这座标志性建筑令人印象深刻。
    我们在塔下拍了很多照片，享受了美妙的景色。塔顶的景观令人叹为观止。
    """

    with open(narrative_file, "w", encoding="utf-8") as f:
        f.write(base_narrative * 10)  # Repeat to reach ~10000 words

    yield project_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def benchmark_report():
    """Generate and store benchmark report."""
    report = {
        "timestamp": time.time(),
        "tests": {},
        "summary": {},
    }
    return report


def record_metric(metrics: Dict, key: str, value):
    """Record a performance metric."""
    metrics[key] = value


def calculate_duration(metrics: Dict) -> float:
    """Calculate test duration from metrics."""
    if metrics["start_time"] and metrics["end_time"]:
        metrics["duration"] = metrics["end_time"] - metrics["start_time"]
        return metrics["duration"]
    return 0


def save_benchmark_report(report: Dict, output_file: str):
    """Save benchmark report to JSON file."""
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
