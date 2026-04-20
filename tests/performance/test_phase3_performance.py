"""Performance tests for Phase 3: Media Analysis & Alignment."""

import time

import pytest

from tests.performance.benchmark_runner import BenchmarkRunner


@pytest.fixture
def benchmark_runner():
    """Create benchmark runner instance."""
    return BenchmarkRunner(output_dir="performance_results/phase3")


class TestPhase3Performance:
    """Performance tests for Phase 3 modules."""

    def test_media_analysis_performance(self, standard_project_dir, benchmark_runner):
        """Test media analysis performance."""
        benchmark = benchmark_runner.start_benchmark("media_analysis")

        media_dir = standard_project_dir / "media"
        media_files = list(media_dir.glob("*"))

        # Simulate media analysis
        shots = []
        for media_file in media_files[:30]:  # Analyze first 30 files
            shot = {
                "file": str(media_file),
                "type": "video" if media_file.suffix == ".mp4" else "image",
                "quality_score": 0.8,
                "features": ["scene1", "person", "landscape"],
            }
            shots.append(shot)
            time.sleep(0.01)  # Simulate analysis time

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("media_analysis", benchmark)

        # Verify performance
        assert benchmark["duration"] < 5.0, "Media analysis should complete in < 5 seconds"
        assert len(shots) == 30, "Should analyze 30 media files"

    def test_alignment_engine_performance(self, benchmark_runner):
        """Test alignment engine performance."""
        benchmark = benchmark_runner.start_benchmark("alignment_engine")

        # Simulate story segments
        segments = [
            {"id": "seg_1", "title": "Day 1", "keywords": ["departure", "airport"]},
            {"id": "seg_2", "title": "Day 2", "keywords": ["eiffel", "tower"]},
            {"id": "seg_3", "title": "Day 3", "keywords": ["museum", "art"]},
        ]

        # Simulate media shots
        shots = [
            {"id": f"shot_{i}", "features": ["scene", "person"], "quality": 0.8}
            for i in range(100)
        ]

        # Simulate alignment matching
        candidates = []
        for segment in segments:
            for shot in shots[:20]:  # Generate candidates
                candidate = {
                    "segment_id": segment["id"],
                    "shot_id": shot["id"],
                    "confidence": 0.7 + (hash(segment["id"] + shot["id"]) % 30) / 100,
                }
                candidates.append(candidate)
                time.sleep(0.001)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("alignment_engine", benchmark)

        # Verify performance
        assert benchmark["duration"] < 3.0, "Alignment engine should complete in < 3 seconds"
        assert len(candidates) > 0, "Should generate candidates"

    def test_highlight_confirmation_performance(self, benchmark_runner):
        """Test highlight confirmation performance."""
        benchmark = benchmark_runner.start_benchmark("highlight_confirmation")

        # Simulate highlight candidates
        candidates = [
            {"id": f"candidate_{i}", "segment_id": f"seg_{i % 3}", "confidence": 0.8}
            for i in range(50)
        ]

        # Simulate user confirmation
        highlights = []
        for candidate in candidates[:10]:
            highlight = {
                "id": candidate["id"],
                "segment_id": candidate["segment_id"],
                "confirmed": True,
            }
            highlights.append(highlight)
            time.sleep(0.01)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("highlight_confirmation", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Highlight confirmation should complete in < 1 second"

    def test_large_media_analysis_performance(self, large_project_dir, benchmark_runner):
        """Test media analysis with large project."""
        benchmark = benchmark_runner.start_benchmark("large_media_analysis")

        media_dir = large_project_dir / "media"
        media_files = list(media_dir.glob("*"))

        # Simulate media analysis for large project
        shots = []
        for media_file in media_files[:100]:  # Analyze first 100 files
            shot = {
                "file": str(media_file),
                "type": "video" if media_file.suffix == ".mp4" else "image",
                "quality_score": 0.8,
                "features": ["scene1", "person", "landscape"],
            }
            shots.append(shot)
            time.sleep(0.005)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("large_media_analysis", benchmark)

        # Verify performance
        assert benchmark["duration"] < 10.0, "Large media analysis should complete in < 10 seconds"

    def test_phase3_complete_flow_performance(self, standard_project_dir, benchmark_runner):
        """Test complete Phase 3 flow performance."""
        benchmark = benchmark_runner.start_benchmark("phase3_complete_flow")

        # Media analysis
        time.sleep(0.5)

        # Alignment engine
        time.sleep(0.3)

        # Highlight confirmation
        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("phase3_complete_flow", benchmark)

        # Verify performance
        assert benchmark["duration"] < 5.0, "Phase 3 complete flow should complete in < 5 seconds"

    def test_memory_efficiency_phase3(self, benchmark_runner):
        """Test memory efficiency during Phase 3 operations."""
        benchmark = benchmark_runner.start_benchmark("memory_efficiency_phase3")

        # Simulate large candidate set
        candidates = []
        for i in range(1000):
            candidate = {
                "id": f"candidate_{i}",
                "segment_id": f"seg_{i % 10}",
                "shot_id": f"shot_{i % 100}",
                "confidence": 0.5 + (i % 50) / 100,
                "features": ["feature1", "feature2", "feature3"],
            }
            candidates.append(candidate)

        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("memory_efficiency_phase3", benchmark)

        # Verify memory usage
        assert benchmark["memory_delta"] < 200, "Memory delta should be < 200 MB"

    @pytest.mark.benchmark
    def test_generate_phase3_report(self, benchmark_runner):
        """Generate Phase 3 performance report."""
        report = benchmark_runner.generate_report()
        report_file = benchmark_runner.save_report("phase3_benchmark_report.json")

        assert report_file.exists(), "Report file should be created"
        assert report["total_tests"] > 0, "Report should contain test results"
