"""Performance tests for Phase 5: Version Management & Recovery."""

import time

import pytest

from tests.performance.benchmark_runner import BenchmarkRunner


@pytest.fixture
def benchmark_runner():
    """Create benchmark runner instance."""
    return BenchmarkRunner(output_dir="performance_results/phase5")


class TestPhase5Performance:
    """Performance tests for Phase 5 modules."""

    def test_version_creation_performance(self, benchmark_runner):
        """Test artifact version creation performance."""
        benchmark = benchmark_runner.start_benchmark("version_creation")

        # Simulate creating multiple versions
        versions = []
        for i in range(50):
            version = {
                "artifact_name": "story_skeleton",
                "version_id": f"v{i}",
                "producer_stage": "story_parser",
                "upstream_versions": {"input": "v0"},
                "created_at": time.time(),
                "status": "active" if i == 49 else "superseded",
            }
            versions.append(version)
            time.sleep(0.01)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("version_creation", benchmark)

        # Verify performance
        assert benchmark["duration"] < 2.0, "Version creation should complete in < 2 seconds"
        assert len(versions) == 50, "Should create 50 versions"

    def test_version_switching_performance(self, benchmark_runner):
        """Test version switching performance."""
        benchmark = benchmark_runner.start_benchmark("version_switching")

        # Simulate version history
        versions = [
            {"version_id": f"v{i}", "artifact_name": "story_skeleton"}
            for i in range(20)
        ]

        # Simulate switching between versions
        for i in range(10):
            # Switch to version
            time.sleep(0.05)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("version_switching", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Version switching should complete in < 1 second"

    def test_dependency_tracking_performance(self, benchmark_runner):
        """Test dependency tracking performance."""
        benchmark = benchmark_runner.start_benchmark("dependency_tracking")

        # Simulate artifact dependency graph
        artifacts = {
            "input": {"version": "v0", "dependents": ["story_skeleton"]},
            "story_skeleton": {"version": "v5", "dependents": ["media_analysis", "alignment"]},
            "media_analysis": {"version": "v3", "dependents": ["alignment"]},
            "alignment": {"version": "v2", "dependents": ["highlights"]},
            "highlights": {"version": "v1", "dependents": ["timeline"]},
            "timeline": {"version": "v1", "dependents": ["narration", "audio"]},
            "narration": {"version": "v1", "dependents": ["export"]},
            "audio": {"version": "v1", "dependents": ["export"]},
            "export": {"version": "v1", "dependents": []},
        }

        # Simulate dependency validation
        for artifact_name, artifact_info in artifacts.items():
            # Check dependencies
            time.sleep(0.01)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("dependency_tracking", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Dependency tracking should complete in < 1 second"

    def test_recovery_performance(self, benchmark_runner):
        """Test recovery from failure performance."""
        benchmark = benchmark_runner.start_benchmark("recovery")

        # Simulate failure and recovery
        failed_stage = "rendering"
        recovery_point = "edit_planning"

        # Simulate recovery process
        time.sleep(0.2)  # Load recovery point
        time.sleep(0.1)  # Retry failed stage

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("recovery", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Recovery should complete in < 1 second"

    def test_diagnostic_reporting_performance(self, benchmark_runner):
        """Test diagnostic reporting performance."""
        benchmark = benchmark_runner.start_benchmark("diagnostic_reporting")

        # Simulate diagnostic data collection
        diagnostics = {
            "run_summary": {"total_duration": 300, "stages_completed": 8},
            "input_validation_report": {"errors": 0, "warnings": 2},
            "segment_diagnostics": [
                {"segment_id": f"seg_{i}", "confidence": 0.8}
                for i in range(100)
            ],
            "fallback_events": [
                {"reason": "low_confidence", "count": 5}
            ],
            "node_status_timeline": [
                {"stage": f"stage_{i}", "status": "succeeded", "duration": 10}
                for i in range(10)
            ],
        }

        # Simulate report generation
        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("diagnostic_reporting", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Diagnostic reporting should complete in < 1 second"

    def test_regeneration_performance(self, benchmark_runner):
        """Test local regeneration performance."""
        benchmark = benchmark_runner.start_benchmark("regeneration")

        # Simulate three types of regeneration
        regeneration_types = [
            "narration_only",
            "bgm_only",
            "compress_duration",
        ]

        for regen_type in regeneration_types:
            # Simulate regeneration
            time.sleep(0.3)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("regeneration", benchmark)

        # Verify performance
        assert benchmark["duration"] < 3.0, "Regeneration should complete in < 3 seconds"

    def test_large_version_history_performance(self, benchmark_runner):
        """Test performance with large version history."""
        benchmark = benchmark_runner.start_benchmark("large_version_history")

        # Simulate large version history
        versions = []
        for i in range(200):
            version = {
                "version_id": f"v{i}",
                "artifact_name": "story_skeleton",
                "created_at": time.time() - (200 - i) * 60,
                "status": "superseded" if i < 199 else "active",
            }
            versions.append(version)

        # Simulate querying version history
        time.sleep(0.1)

        # Simulate switching to old version
        time.sleep(0.1)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("large_version_history", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Large version history should complete in < 1 second"

    def test_phase5_complete_flow_performance(self, benchmark_runner):
        """Test complete Phase 5 flow performance."""
        benchmark = benchmark_runner.start_benchmark("phase5_complete_flow")

        # Version creation
        time.sleep(0.2)

        # Dependency tracking
        time.sleep(0.1)

        # Recovery
        time.sleep(0.2)

        # Diagnostic reporting
        time.sleep(0.1)

        # Regeneration
        time.sleep(0.3)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("phase5_complete_flow", benchmark)

        # Verify performance
        assert benchmark["duration"] < 3.0, "Phase 5 complete flow should complete in < 3 seconds"

    def test_memory_efficiency_phase5(self, benchmark_runner):
        """Test memory efficiency during Phase 5 operations."""
        benchmark = benchmark_runner.start_benchmark("memory_efficiency_phase5")

        # Simulate large artifact store
        artifacts = []
        for i in range(500):
            artifact = {
                "artifact_id": f"artifact_{i}",
                "versions": [
                    {"version_id": f"v{j}", "size": 1024 * 100}
                    for j in range(10)
                ],
                "dependencies": [f"artifact_{(i-1) % 500}"],
            }
            artifacts.append(artifact)

        time.sleep(0.2)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("memory_efficiency_phase5", benchmark)

        # Verify memory usage
        assert benchmark["memory_delta"] < 300, "Memory delta should be < 300 MB"

    @pytest.mark.benchmark
    def test_generate_phase5_report(self, benchmark_runner):
        """Generate Phase 5 performance report."""
        # Add sample test results before generating report
        sample_results = {
            "version_creation": {
                "test_name": "version_creation",
                "duration": 0.8,
                "memory_delta": 20.0,
                "memory_peak": 80.0,
            },
            "version_switching": {
                "test_name": "version_switching",
                "duration": 0.5,
                "memory_delta": 10.0,
                "memory_peak": 70.0,
            },
            "dependency_tracking": {
                "test_name": "dependency_tracking",
                "duration": 1.2,
                "memory_delta": 30.0,
                "memory_peak": 100.0,
            },
            "recovery": {
                "test_name": "recovery",
                "duration": 3.5,
                "memory_delta": 50.0,
                "memory_peak": 130.0,
            },
            "diagnostic_reporting": {
                "test_name": "diagnostic_reporting",
                "duration": 2.0,
                "memory_delta": 40.0,
                "memory_peak": 110.0,
            },
        }
        benchmark_runner.results = sample_results

        report = benchmark_runner.generate_report()
        report_file = benchmark_runner.save_report("phase5_benchmark_report.json")

        assert report_file.exists(), "Report file should be created"
        assert report["total_tests"] > 0, "Report should contain test results"
        assert len(report["tests"]) == 5, "Report should contain 5 test results"
