"""Benchmark runner for performance testing."""

import json
import time
from pathlib import Path
from typing import Dict, List

import psutil


class BenchmarkRunner:
    """Run and collect performance benchmarks."""

    def __init__(self, output_dir: str = "performance_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
        self.process = psutil.Process()

    def start_benchmark(self, test_name: str) -> Dict:
        """Start a benchmark measurement."""
        return {
            "test_name": test_name,
            "start_time": time.time(),
            "start_memory": self.process.memory_info().rss / 1024 / 1024,  # MB
            "start_cpu_percent": self.process.cpu_percent(),
        }

    def end_benchmark(self, benchmark: Dict) -> Dict:
        """End a benchmark measurement and calculate metrics."""
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        benchmark["end_time"] = end_time
        benchmark["end_memory"] = end_memory
        benchmark["duration"] = end_time - benchmark["start_time"]
        benchmark["memory_delta"] = end_memory - benchmark["start_memory"]
        benchmark["memory_peak"] = end_memory  # Simplified, should use tracemalloc for accuracy

        return benchmark

    def record_result(self, test_name: str, benchmark: Dict):
        """Record benchmark result."""
        self.results[test_name] = benchmark

    def generate_report(self) -> Dict:
        """Generate performance report."""
        report = {
            "timestamp": time.time(),
            "total_tests": len(self.results),
            "tests": self.results,
            "summary": self._calculate_summary(),
        }
        return report

    def _calculate_summary(self) -> Dict:
        """Calculate summary statistics."""
        if not self.results:
            return {}

        durations = [r["duration"] for r in self.results.values()]
        memory_deltas = [r["memory_delta"] for r in self.results.values()]

        return {
            "total_duration": sum(durations),
            "avg_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "total_memory_delta": sum(memory_deltas),
            "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "max_memory_delta": max(memory_deltas),
        }

    def save_report(self, filename: str = "benchmark_report.json"):
        """Save report to file."""
        report = self.generate_report()
        output_file = self.output_dir / filename
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        return output_file

    def compare_with_baseline(self, baseline_file: str) -> Dict:
        """Compare current results with baseline."""
        if not Path(baseline_file).exists():
            return {"status": "no_baseline"}

        with open(baseline_file, "r") as f:
            baseline = json.load(f)

        comparison = {
            "baseline_timestamp": baseline.get("timestamp"),
            "current_timestamp": time.time(),
            "tests": {},
        }

        for test_name, current_result in self.results.items():
            if test_name in baseline.get("tests", {}):
                baseline_result = baseline["tests"][test_name]
                comparison["tests"][test_name] = {
                    "baseline_duration": baseline_result.get("duration"),
                    "current_duration": current_result.get("duration"),
                    "duration_change_percent": (
                        (current_result.get("duration", 0) - baseline_result.get("duration", 0))
                        / baseline_result.get("duration", 1)
                        * 100
                    ),
                    "baseline_memory": baseline_result.get("memory_delta"),
                    "current_memory": current_result.get("memory_delta"),
                    "memory_change_percent": (
                        (current_result.get("memory_delta", 0) - baseline_result.get("memory_delta", 0))
                        / baseline_result.get("memory_delta", 1)
                        * 100
                    ),
                }

        return comparison
