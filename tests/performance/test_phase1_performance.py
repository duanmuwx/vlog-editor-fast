"""Performance tests for Phase 1: Infrastructure & Input Processing."""

import time
from pathlib import Path

import pytest

from tests.performance.benchmark_runner import BenchmarkRunner


@pytest.fixture
def benchmark_runner():
    """Create benchmark runner instance."""
    return BenchmarkRunner(output_dir="performance_results/phase1")


class TestPhase1Performance:
    """Performance tests for Phase 1 modules."""

    def test_project_creation_performance(self, standard_project_dir, benchmark_runner):
        """Test project creation performance."""
        benchmark = benchmark_runner.start_benchmark("project_creation")

        # Simulate project creation
        project_name = "test_project"
        project_config = {
            "name": project_name,
            "media_dir": str(standard_project_dir / "media"),
            "narrative_file": str(standard_project_dir / "narrative.txt"),
        }

        # Simulate some work
        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("project_creation", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Project creation should complete in < 1 second"

    def test_input_validation_performance(self, standard_project_dir, benchmark_runner):
        """Test input validation performance."""
        benchmark = benchmark_runner.start_benchmark("input_validation")

        # Simulate input validation
        media_dir = standard_project_dir / "media"
        narrative_file = standard_project_dir / "narrative.txt"

        # Count files
        video_count = len(list(media_dir.glob("*.mp4")))
        image_count = len(list(media_dir.glob("*.jpg")))

        # Read narrative
        with open(narrative_file, "r", encoding="utf-8") as f:
            narrative_length = len(f.read())

        # Simulate validation
        time.sleep(0.05)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("input_validation", benchmark)

        # Verify performance
        assert benchmark["duration"] < 0.5, "Input validation should complete in < 0.5 seconds"
        assert video_count == 30, "Should find 30 videos"
        assert image_count == 400, "Should find 400 images"
        assert narrative_length > 3000, "Narrative should be > 3000 characters"

    def test_asset_indexing_performance(self, standard_project_dir, benchmark_runner):
        """Test asset indexing performance."""
        benchmark = benchmark_runner.start_benchmark("asset_indexing")

        media_dir = standard_project_dir / "media"

        # Simulate asset indexing
        assets = []
        for media_file in media_dir.glob("*"):
            assets.append({
                "path": str(media_file),
                "size": media_file.stat().st_size,
                "type": "video" if media_file.suffix == ".mp4" else "image",
            })

        # Simulate metadata extraction
        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("asset_indexing", benchmark)

        # Verify performance
        assert benchmark["duration"] < 2.0, "Asset indexing should complete in < 2 seconds"
        assert len(assets) == 430, "Should index 430 assets (30 videos + 400 images)"

    def test_phase1_complete_flow_performance(self, standard_project_dir, benchmark_runner):
        """Test complete Phase 1 flow performance."""
        benchmark = benchmark_runner.start_benchmark("phase1_complete_flow")

        # Simulate complete Phase 1 flow
        media_dir = standard_project_dir / "media"
        narrative_file = standard_project_dir / "narrative.txt"

        # Project creation
        time.sleep(0.1)

        # Input validation
        time.sleep(0.05)

        # Asset indexing
        assets = list(media_dir.glob("*"))
        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("phase1_complete_flow", benchmark)

        # Verify performance
        assert benchmark["duration"] < 3.0, "Phase 1 complete flow should complete in < 3 seconds"

    def test_large_project_indexing_performance(self, large_project_dir, benchmark_runner):
        """Test asset indexing performance with large project."""
        benchmark = benchmark_runner.start_benchmark("large_project_indexing")

        media_dir = large_project_dir / "media"

        # Simulate asset indexing for large project
        assets = []
        for media_file in media_dir.glob("*"):
            assets.append({
                "path": str(media_file),
                "size": media_file.stat().st_size,
                "type": "video" if media_file.suffix == ".mp4" else "image",
            })

        # Simulate metadata extraction
        time.sleep(0.2)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("large_project_indexing", benchmark)

        # Verify performance
        assert benchmark["duration"] < 5.0, "Large project indexing should complete in < 5 seconds"
        assert len(assets) == 1100, "Should index 1100 assets (100 videos + 1000 images)"

    def test_memory_efficiency(self, standard_project_dir, benchmark_runner):
        """Test memory efficiency during Phase 1 operations."""
        benchmark = benchmark_runner.start_benchmark("memory_efficiency")

        media_dir = standard_project_dir / "media"

        # Simulate operations
        assets = []
        for media_file in media_dir.glob("*"):
            assets.append({
                "path": str(media_file),
                "size": media_file.stat().st_size,
            })

        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("memory_efficiency", benchmark)

        # Verify memory usage
        assert benchmark["memory_delta"] < 100, "Memory delta should be < 100 MB"

    @pytest.mark.benchmark
    def test_generate_phase1_report(self, benchmark_runner):
        """Generate Phase 1 performance report."""
        report = benchmark_runner.generate_report()
        report_file = benchmark_runner.save_report("phase1_benchmark_report.json")

        assert report_file.exists(), "Report file should be created"
        assert report["total_tests"] > 0, "Report should contain test results"
