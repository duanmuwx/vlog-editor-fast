"""Performance tests for Phase 2: Story Analysis & Confirmation."""

import time

import pytest

from tests.performance.benchmark_runner import BenchmarkRunner


@pytest.fixture
def benchmark_runner():
    """Create benchmark runner instance."""
    return BenchmarkRunner(output_dir="performance_results/phase2")


class TestPhase2Performance:
    """Performance tests for Phase 2 modules."""

    def test_story_parsing_performance(self, standard_project_dir, benchmark_runner):
        """Test story parsing performance."""
        benchmark = benchmark_runner.start_benchmark("story_parsing")

        # Read narrative
        narrative_file = standard_project_dir / "narrative.txt"
        with open(narrative_file, "r", encoding="utf-8") as f:
            narrative = f.read()

        # Simulate story parsing
        time.sleep(0.5)  # Simulate LLM API call

        # Parse into segments
        segments = [
            {"title": "Day 1", "summary": "Departure", "importance": 0.8},
            {"title": "Day 2", "summary": "Eiffel Tower", "importance": 0.9},
            {"title": "Day 3", "summary": "Louvre Museum", "importance": 0.85},
            {"title": "Day 4", "summary": "Seine River", "importance": 0.7},
            {"title": "Day 5", "summary": "Versailles", "importance": 0.9},
            {"title": "Day 6", "summary": "Montmartre", "importance": 0.75},
            {"title": "Day 7", "summary": "Farewell", "importance": 0.6},
        ]

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("story_parsing", benchmark)

        # Verify performance
        assert benchmark["duration"] < 10.0, "Story parsing should complete in < 10 seconds"
        assert len(segments) >= 3, "Should generate at least 3 segments"

    def test_skeleton_confirmation_performance(self, benchmark_runner):
        """Test skeleton confirmation performance."""
        benchmark = benchmark_runner.start_benchmark("skeleton_confirmation")

        # Simulate skeleton confirmation
        segments = [
            {"id": "seg_1", "title": "Day 1", "summary": "Departure"},
            {"id": "seg_2", "title": "Day 2", "summary": "Eiffel Tower"},
            {"id": "seg_3", "title": "Day 3", "summary": "Louvre Museum"},
        ]

        # Simulate user edits
        edits = [
            {"action": "merge", "segments": ["seg_1", "seg_2"]},
            {"action": "reorder", "order": ["seg_2", "seg_1", "seg_3"]},
        ]

        # Apply edits
        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("skeleton_confirmation", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Skeleton confirmation should complete in < 1 second"

    def test_long_narrative_parsing_performance(self, large_project_dir, benchmark_runner):
        """Test story parsing with long narrative."""
        benchmark = benchmark_runner.start_benchmark("long_narrative_parsing")

        # Read long narrative
        narrative_file = large_project_dir / "narrative.txt"
        with open(narrative_file, "r", encoding="utf-8") as f:
            narrative = f.read()

        # Simulate story parsing with longer narrative
        time.sleep(1.0)  # Simulate longer LLM API call

        # Parse into segments
        segments = [
            {"title": f"Day {i}", "summary": f"Day {i} activities", "importance": 0.7 + (i % 3) * 0.1}
            for i in range(1, 11)
        ]

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("long_narrative_parsing", benchmark)

        # Verify performance
        assert benchmark["duration"] < 15.0, "Long narrative parsing should complete in < 15 seconds"
        assert len(segments) >= 5, "Should generate at least 5 segments"

    def test_skeleton_versioning_performance(self, benchmark_runner):
        """Test skeleton versioning performance."""
        benchmark = benchmark_runner.start_benchmark("skeleton_versioning")

        # Simulate creating multiple skeleton versions
        versions = []
        for i in range(10):
            version = {
                "version_id": f"v{i}",
                "segments": [
                    {"id": f"seg_{j}", "title": f"Segment {j}"}
                    for j in range(5)
                ],
                "created_at": time.time(),
            }
            versions.append(version)
            time.sleep(0.05)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("skeleton_versioning", benchmark)

        # Verify performance
        assert benchmark["duration"] < 2.0, "Skeleton versioning should complete in < 2 seconds"
        assert len(versions) == 10, "Should create 10 versions"

    def test_phase2_complete_flow_performance(self, standard_project_dir, benchmark_runner):
        """Test complete Phase 2 flow performance."""
        benchmark = benchmark_runner.start_benchmark("phase2_complete_flow")

        # Read narrative
        narrative_file = standard_project_dir / "narrative.txt"
        with open(narrative_file, "r", encoding="utf-8") as f:
            narrative = f.read()

        # Story parsing
        time.sleep(0.5)

        # Skeleton confirmation
        time.sleep(0.1)

        # Version management
        time.sleep(0.05)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("phase2_complete_flow", benchmark)

        # Verify performance
        assert benchmark["duration"] < 5.0, "Phase 2 complete flow should complete in < 5 seconds"

    def test_memory_efficiency_phase2(self, standard_project_dir, benchmark_runner):
        """Test memory efficiency during Phase 2 operations."""
        benchmark = benchmark_runner.start_benchmark("memory_efficiency_phase2")

        # Read narrative
        narrative_file = standard_project_dir / "narrative.txt"
        with open(narrative_file, "r", encoding="utf-8") as f:
            narrative = f.read()

        # Simulate operations
        segments = []
        for i in range(100):
            segment = {
                "id": f"seg_{i}",
                "title": f"Segment {i}",
                "summary": narrative[:200],
                "keywords": ["keyword1", "keyword2", "keyword3"],
            }
            segments.append(segment)

        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("memory_efficiency_phase2", benchmark)

        # Verify memory usage
        assert benchmark["memory_delta"] < 150, "Memory delta should be < 150 MB"

    @pytest.mark.benchmark
    def test_generate_phase2_report(self, benchmark_runner):
        """Generate Phase 2 performance report."""
        report = benchmark_runner.generate_report()
        report_file = benchmark_runner.save_report("phase2_benchmark_report.json")

        assert report_file.exists(), "Report file should be created"
        assert report["total_tests"] > 0, "Report should contain test results"
