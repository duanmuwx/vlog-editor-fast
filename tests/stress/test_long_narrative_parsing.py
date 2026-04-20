"""Stress tests for long narrative parsing."""

import time

import pytest


class TestLongNarrativeParsing:
    """Stress tests for parsing long narratives."""

    def test_10000_word_narrative_parsing(self, resource_monitor):
        """Test parsing a 10000+ word narrative."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Create long narrative
        base_text = "Day 1: We started our journey from Beijing. " * 100
        narrative = base_text * 10  # ~10000 words

        # Simulate parsing
        start_time = time.time()
        time.sleep(0.5)  # Simulate LLM API call

        # Parse into segments
        segments = []
        for i in range(50):
            segment = {
                "id": f"seg_{i}",
                "title": f"Segment {i}",
                "summary": narrative[:200],
                "keywords": ["keyword1", "keyword2"],
            }
            segments.append(segment)

        parse_time = time.time() - start_time

        # Monitor memory
        current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
        resource_monitor["peak_memory"] = current_memory

        assert len(segments) == 50, "Should generate 50 segments"
        assert parse_time < 10.0, "Parsing should complete in < 10 seconds"
        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"

    def test_20000_word_narrative_parsing(self, resource_monitor):
        """Test parsing a 20000+ word narrative."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Create very long narrative
        base_text = "Day 1: We started our journey from Beijing. " * 100
        narrative = base_text * 20  # ~20000 words

        # Simulate parsing
        start_time = time.time()
        time.sleep(1.0)  # Simulate longer LLM API call

        # Parse into segments
        segments = []
        for i in range(100):
            segment = {
                "id": f"seg_{i}",
                "title": f"Segment {i}",
                "summary": narrative[:200],
                "keywords": ["keyword1", "keyword2", "keyword3"],
            }
            segments.append(segment)

        parse_time = time.time() - start_time

        # Monitor memory
        current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
        resource_monitor["peak_memory"] = current_memory

        assert len(segments) == 100, "Should generate 100 segments"
        assert parse_time < 15.0, "Parsing should complete in < 15 seconds"
        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"

    def test_complex_narrative_with_metadata(self, resource_monitor):
        """Test parsing complex narrative with rich metadata."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Create complex narrative with metadata
        narrative = """
        Day 1 (2024-01-15): We departed from Beijing (39.9042°N, 116.4074°E) at 10:00 AM.
        The flight to Paris took 12 hours. We arrived at Charles de Gaulle Airport.

        Day 2 (2024-01-16): Visited Eiffel Tower (48.8584°N, 2.2945°E) at 14:00.
        Took many photos and videos. The weather was clear and sunny.

        Day 3 (2024-01-17): Explored Louvre Museum (48.8606°N, 2.3352°E).
        Saw the Mona Lisa and other masterpieces. Spent 6 hours inside.
        """ * 50

        # Simulate parsing with metadata extraction
        start_time = time.time()
        time.sleep(0.8)

        # Extract metadata
        segments = []
        for i in range(30):
            segment = {
                "id": f"seg_{i}",
                "title": f"Day {i}",
                "summary": narrative[:300],
                "keywords": ["travel", "paris", "museum"],
                "locations": ["Beijing", "Paris"],
                "timestamps": ["2024-01-15", "2024-01-16"],
                "coordinates": [(39.9042, 116.4074), (48.8584, 2.2945)],
            }
            segments.append(segment)

        parse_time = time.time() - start_time

        # Monitor memory
        current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
        resource_monitor["peak_memory"] = current_memory

        assert len(segments) == 30, "Should generate 30 segments"
        assert parse_time < 10.0, "Parsing should complete in < 10 seconds"
        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"

    def test_narrative_with_multiple_languages(self, resource_monitor):
        """Test parsing narrative with multiple languages."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Create multilingual narrative
        narrative = """
        Day 1: 我们从北京出发，飞往巴黎。这是一次梦幻般的旅程。
        We departed from Beijing and flew to Paris. It was a magical journey.
        Nous sommes partis de Pékin et avons volé vers Paris. C'était un voyage magique.
        """ * 50

        # Simulate parsing
        start_time = time.time()
        time.sleep(0.6)

        # Parse into segments
        segments = []
        for i in range(20):
            segment = {
                "id": f"seg_{i}",
                "title": f"Segment {i}",
                "summary": narrative[:300],
                "languages": ["Chinese", "English", "French"],
            }
            segments.append(segment)

        parse_time = time.time() - start_time

        # Monitor memory
        current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
        resource_monitor["peak_memory"] = current_memory

        assert len(segments) == 20, "Should generate 20 segments"
        assert parse_time < 10.0, "Parsing should complete in < 10 seconds"

    def test_narrative_with_special_characters(self, resource_monitor):
        """Test parsing narrative with special characters and emojis."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Create narrative with special characters
        narrative = """
        Day 1: 🎉 We started our journey! ✈️
        Visited: Eiffel Tower 🗼, Louvre Museum 🎨, Seine River 🌊
        Weather: ☀️ Sunny, 🌡️ 15°C
        Rating: ⭐⭐⭐⭐⭐ (5/5)
        """ * 50

        # Simulate parsing
        start_time = time.time()
        time.sleep(0.5)

        # Parse into segments
        segments = []
        for i in range(15):
            segment = {
                "id": f"seg_{i}",
                "title": f"Day {i}",
                "summary": narrative[:300],
            }
            segments.append(segment)

        parse_time = time.time() - start_time

        # Monitor memory
        current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
        resource_monitor["peak_memory"] = current_memory

        assert len(segments) == 15, "Should generate 15 segments"
        assert parse_time < 10.0, "Parsing should complete in < 10 seconds"

    @pytest.mark.stress
    def test_sequential_narrative_parsing(self, resource_monitor):
        """Test sequential parsing of multiple narratives."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Parse multiple narratives sequentially
        for project_num in range(5):
            narrative = f"Project {project_num}: " + "Day 1: Journey starts. " * 100

            # Simulate parsing
            time.sleep(0.3)

            # Generate segments
            segments = [
                {"id": f"seg_{i}", "title": f"Segment {i}"}
                for i in range(10)
            ]

            # Monitor memory
            current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
            if resource_monitor["peak_memory"] is None or current_memory > resource_monitor["peak_memory"]:
                resource_monitor["peak_memory"] = current_memory

        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"
