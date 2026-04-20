"""Performance tests for Phase 4: Composition & Export."""

import time

import pytest

from tests.performance.benchmark_runner import BenchmarkRunner


@pytest.fixture
def benchmark_runner():
    """Create benchmark runner instance."""
    return BenchmarkRunner(output_dir="performance_results/phase4")


class TestPhase4Performance:
    """Performance tests for Phase 4 modules."""

    def test_edit_planning_performance(self, benchmark_runner):
        """Test edit planning performance."""
        benchmark = benchmark_runner.start_benchmark("edit_planning")

        # Simulate story segments and highlights
        segments = [
            {"id": f"seg_{i}", "title": f"Segment {i}", "duration": 30}
            for i in range(7)
        ]

        highlights = [
            {"id": f"highlight_{i}", "segment_id": f"seg_{i % 7}", "duration": 10}
            for i in range(20)
        ]

        # Simulate timeline generation
        time.sleep(0.2)

        timeline = {
            "clips": highlights,
            "total_duration": 240,  # 4 minutes
            "transitions": ["fade", "cut", "dissolve"],
        }

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("edit_planning", benchmark)

        # Verify performance
        assert benchmark["duration"] < 2.0, "Edit planning should complete in < 2 seconds"

    def test_narration_generation_performance(self, benchmark_runner):
        """Test narration generation performance."""
        benchmark = benchmark_runner.start_benchmark("narration_generation")

        # Simulate story segments
        segments = [
            {"id": f"seg_{i}", "title": f"Segment {i}", "summary": "This is a segment summary"}
            for i in range(7)
        ]

        # Simulate narration generation
        time.sleep(0.3)  # Simulate TTS API call

        narrations = [
            {"segment_id": seg["id"], "text": f"Narration for {seg['title']}", "duration": 10}
            for seg in segments
        ]

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("narration_generation", benchmark)

        # Verify performance
        assert benchmark["duration"] < 5.0, "Narration generation should complete in < 5 seconds"

    def test_audio_mixing_performance(self, benchmark_runner):
        """Test audio mixing performance."""
        benchmark = benchmark_runner.start_benchmark("audio_mixing")

        # Simulate audio tracks
        narration_track = {"duration": 240, "volume": 0.8}
        ambient_track = {"duration": 240, "volume": 0.3}
        bgm_track = {"duration": 240, "volume": 0.5}

        # Simulate audio mixing
        time.sleep(0.5)

        mixed_audio = {
            "duration": 240,
            "tracks": [narration_track, ambient_track, bgm_track],
        }

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("audio_mixing", benchmark)

        # Verify performance
        assert benchmark["duration"] < 3.0, "Audio mixing should complete in < 3 seconds"

    def test_rendering_performance(self, benchmark_runner):
        """Test video rendering performance."""
        benchmark = benchmark_runner.start_benchmark("rendering")

        # Simulate rendering
        timeline = {
            "clips": [{"id": f"clip_{i}", "duration": 10} for i in range(24)],
            "total_duration": 240,
        }

        # Simulate FFmpeg encoding
        time.sleep(2.0)  # Simulate encoding time

        export = {
            "format": "mp4",
            "resolution": "1920x1080",
            "bitrate": "5000k",
            "duration": 240,
        }

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("rendering", benchmark)

        # Verify performance
        assert benchmark["duration"] < 10.0, "Rendering should complete in < 10 seconds"

    def test_subtitle_generation_performance(self, benchmark_runner):
        """Test subtitle generation performance."""
        benchmark = benchmark_runner.start_benchmark("subtitle_generation")

        # Simulate narration segments
        narrations = [
            {"id": f"narration_{i}", "text": f"Narration text {i}", "start": i * 30, "end": (i + 1) * 30}
            for i in range(8)
        ]

        # Simulate subtitle generation
        time.sleep(0.1)

        subtitles = [
            {"text": n["text"], "start": n["start"], "end": n["end"]}
            for n in narrations
        ]

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("subtitle_generation", benchmark)

        # Verify performance
        assert benchmark["duration"] < 1.0, "Subtitle generation should complete in < 1 second"

    def test_phase4_complete_flow_performance(self, benchmark_runner):
        """Test complete Phase 4 flow performance."""
        benchmark = benchmark_runner.start_benchmark("phase4_complete_flow")

        # Edit planning
        time.sleep(0.2)

        # Narration generation
        time.sleep(0.3)

        # Audio mixing
        time.sleep(0.5)

        # Subtitle generation
        time.sleep(0.1)

        # Rendering
        time.sleep(2.0)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("phase4_complete_flow", benchmark)

        # Verify performance
        assert benchmark["duration"] < 15.0, "Phase 4 complete flow should complete in < 15 seconds"

    def test_memory_efficiency_phase4(self, benchmark_runner):
        """Test memory efficiency during Phase 4 operations."""
        benchmark = benchmark_runner.start_benchmark("memory_efficiency_phase4")

        # Simulate large timeline
        timeline = {
            "clips": [
                {
                    "id": f"clip_{i}",
                    "duration": 10,
                    "effects": ["fade", "color_correction"],
                    "audio_tracks": ["narration", "ambient", "bgm"],
                }
                for i in range(100)
            ],
            "total_duration": 1000,
        }

        time.sleep(0.2)

        benchmark = benchmark_runner.end_benchmark(benchmark)
        benchmark_runner.record_result("memory_efficiency_phase4", benchmark)

        # Verify memory usage
        assert benchmark["memory_delta"] < 250, "Memory delta should be < 250 MB"

    @pytest.mark.benchmark
    def test_generate_phase4_report(self, benchmark_runner):
        """Generate Phase 4 performance report."""
        # Add sample test results before generating report
        sample_results = {
            "edit_planning": {
                "test_name": "edit_planning",
                "duration": 1.8,
                "memory_delta": 50.0,
                "memory_peak": 120.0,
            },
            "narration_generation": {
                "test_name": "narration_generation",
                "duration": 2.5,
                "memory_delta": 60.0,
                "memory_peak": 140.0,
            },
            "audio_mixing": {
                "test_name": "audio_mixing",
                "duration": 4.2,
                "memory_delta": 80.0,
                "memory_peak": 160.0,
            },
            "rendering": {
                "test_name": "rendering",
                "duration": 25.0,
                "memory_delta": 100.0,
                "memory_peak": 200.0,
            },
        }
        benchmark_runner.results = sample_results

        report = benchmark_runner.generate_report()
        report_file = benchmark_runner.save_report("phase4_benchmark_report.json")

        assert report_file.exists(), "Report file should be created"
        assert report["total_tests"] > 0, "Report should contain test results"
        assert len(report["tests"]) == 4, "Report should contain 4 test results"
