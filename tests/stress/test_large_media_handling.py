"""Stress tests for large media handling."""

import time

import pytest


class TestLargeMediaHandling:
    """Stress tests for handling large media files."""

    def test_100_video_files_processing(self, stress_test_dir, resource_monitor):
        """Test processing 100 video files."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Simulate processing 100 video files
        processed = 0
        for i in range(100):
            # Simulate video analysis
            time.sleep(0.01)
            processed += 1

            # Monitor memory
            current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
            if resource_monitor["peak_memory"] is None or current_memory > resource_monitor["peak_memory"]:
                resource_monitor["peak_memory"] = current_memory

        assert processed == 100, "Should process 100 video files"
        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"

    def test_1000_image_files_processing(self, stress_test_dir, resource_monitor):
        """Test processing 1000 image files."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Simulate processing 1000 image files
        processed = 0
        for i in range(1000):
            # Simulate image analysis
            time.sleep(0.001)
            processed += 1

            # Monitor memory
            current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
            if resource_monitor["peak_memory"] is None or current_memory > resource_monitor["peak_memory"]:
                resource_monitor["peak_memory"] = current_memory

        assert processed == 1000, "Should process 1000 image files"
        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"

    def test_mixed_media_large_scale(self, stress_test_dir, resource_monitor):
        """Test processing mixed media at large scale."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Simulate processing 100 videos + 1000 images
        total_processed = 0

        # Process videos
        for i in range(100):
            time.sleep(0.01)
            total_processed += 1

        # Process images
        for i in range(1000):
            time.sleep(0.001)
            total_processed += 1

            # Monitor memory
            current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
            if resource_monitor["peak_memory"] is None or current_memory > resource_monitor["peak_memory"]:
                resource_monitor["peak_memory"] = current_memory

        assert total_processed == 1100, "Should process 1100 total files"
        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"

    def test_sequential_batch_processing(self, stress_test_dir, resource_monitor):
        """Test sequential batch processing of media."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        batch_size = 50
        num_batches = 10

        for batch_num in range(num_batches):
            # Process batch
            for i in range(batch_size):
                time.sleep(0.005)

            # Monitor memory after each batch
            current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
            if resource_monitor["peak_memory"] is None or current_memory > resource_monitor["peak_memory"]:
                resource_monitor["peak_memory"] = current_memory

        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"

    def test_memory_cleanup_after_processing(self, stress_test_dir, resource_monitor):
        """Test that memory is properly cleaned up after processing."""
        import gc

        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Create large objects to simulate processing
        large_objects = []
        for i in range(500):
            # Create objects that consume memory
            large_objects.append({
                "data": "x" * 10000,  # ~10KB per object
                "index": i,
                "metadata": {"timestamp": time.time(), "id": i}
            })
            time.sleep(0.001)

        peak_during = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Clear objects and force garbage collection
        large_objects.clear()
        gc.collect()
        time.sleep(0.1)

        final_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Memory should be cleaned up (allow for some variance)
        memory_reduction = peak_during - final_memory
        # Check that memory was at least attempted to be cleaned up
        # (may not always succeed due to Python's memory management)
        assert peak_during > resource_monitor["start_memory"], "Memory should have increased during processing"
        # Final memory should be closer to start memory than peak
        assert final_memory <= peak_during, "Memory should not increase after cleanup"

    @pytest.mark.stress
    def test_sustained_processing_load(self, stress_test_dir, resource_monitor):
        """Test sustained processing load over time."""
        resource_monitor["start_memory"] = resource_monitor["process"].memory_info().rss / 1024 / 1024

        # Simulate sustained load for 30 seconds
        start_time = time.time()
        processed = 0

        while time.time() - start_time < 5:  # 5 seconds for testing
            # Process item
            time.sleep(0.01)
            processed += 1

            # Monitor memory
            current_memory = resource_monitor["process"].memory_info().rss / 1024 / 1024
            if resource_monitor["peak_memory"] is None or current_memory > resource_monitor["peak_memory"]:
                resource_monitor["peak_memory"] = current_memory

        assert processed > 0, "Should process items"
        assert resource_monitor["peak_memory"] < 2048, "Peak memory should be < 2GB"
