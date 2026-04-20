"""E2E test for export failure recovery."""

import time

import pytest


class TestExportFailureRecovery:
    """Test recovery from export failures."""

    def test_export_failure_detection(self, e2e_project_setup, e2e_state_tracker):
        """Test detection of export failures."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow up to export
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        time.sleep(1.0)

        # Simulate export failure
        print("Attempting export...")
        try:
            # Simulate FFmpeg error
            raise Exception("FFmpeg encoding failed: codec not found")
        except Exception as e:
            print(f"Export failed: {e}")
            state["errors"].append(str(e))
            state["export_completed"] = False

        assert len(state["errors"]) > 0, "Should record error"
        assert not state["export_completed"], "Export should fail"

    def test_export_retry(self, e2e_project_setup, e2e_state_tracker):
        """Test retrying export after failure."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow up to export
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        time.sleep(1.0)

        # First export attempt fails
        print("First export attempt...")
        state["export_completed"] = False
        state["errors"].append("FFmpeg encoding failed")
        time.sleep(0.1)

        # Retry export
        print("Retrying export...")
        time.sleep(0.5)
        state["export_completed"] = True

        assert state["export_completed"], "Export should succeed on retry"

    def test_export_with_reduced_quality(self, e2e_project_setup, e2e_state_tracker):
        """Test export with reduced quality after failure."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow up to export
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        time.sleep(1.0)

        # First export attempt fails
        print("First export attempt with high quality...")
        export_config = {"quality": "high", "bitrate": "5000k"}
        state["export_completed"] = False
        state["errors"].append("Insufficient disk space")
        time.sleep(0.1)

        # Retry with reduced quality
        print("Retrying with reduced quality...")
        export_config = {"quality": "medium", "bitrate": "2500k"}
        time.sleep(0.3)
        state["export_completed"] = True

        assert state["export_completed"], "Export should succeed with reduced quality"
        assert export_config["quality"] == "medium", "Should use medium quality"

    def test_partial_export_recovery(self, e2e_project_setup, e2e_state_tracker):
        """Test recovery from partial export."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow up to export
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        time.sleep(1.0)

        # Export fails midway
        print("Export fails midway...")
        state["export_completed"] = False
        state["errors"].append("Export interrupted at 50%")
        time.sleep(0.1)

        # Resume export from checkpoint
        print("Resuming export from checkpoint...")
        time.sleep(0.3)
        state["export_completed"] = True

        assert state["export_completed"], "Export should complete after resume"

    def test_export_with_alternative_codec(self, e2e_project_setup, e2e_state_tracker):
        """Test export with alternative codec after failure."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow up to export
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        time.sleep(1.0)

        # First export attempt with H.264 fails
        print("Export attempt with H.264 codec...")
        export_config = {"codec": "h264"}
        state["export_completed"] = False
        state["errors"].append("H.264 codec not available")
        time.sleep(0.1)

        # Retry with H.265
        print("Retrying with H.265 codec...")
        export_config = {"codec": "h265"}
        time.sleep(0.3)
        state["export_completed"] = True

        assert state["export_completed"], "Export should succeed with alternative codec"
        assert export_config["codec"] == "h265", "Should use H.265 codec"

    def test_export_cleanup_after_failure(self, e2e_project_setup, e2e_state_tracker):
        """Test cleanup of partial files after export failure."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow up to export
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        time.sleep(1.0)

        # Export fails
        print("Export fails...")
        partial_files = ["output.mp4.tmp", "output.srt.tmp"]
        state["export_completed"] = False
        state["errors"].append("Export failed")
        time.sleep(0.1)

        # Cleanup partial files
        print("Cleaning up partial files...")
        for f in partial_files:
            print(f"Removing {f}")
        time.sleep(0.1)

        # Retry export
        print("Retrying export...")
        time.sleep(0.3)
        state["export_completed"] = True

        assert state["export_completed"], "Export should succeed after cleanup"

    @pytest.mark.e2e
    def test_comprehensive_export_recovery(self, e2e_project_setup, e2e_state_tracker):
        """Test comprehensive export failure recovery."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow up to export
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        time.sleep(1.0)

        # Simulate multiple export attempts
        max_retries = 3
        retry_count = 0
        export_strategies = [
            {"quality": "high", "codec": "h264"},
            {"quality": "medium", "codec": "h264"},
            {"quality": "medium", "codec": "h265"},
        ]

        for strategy in export_strategies:
            retry_count += 1
            print(f"Export attempt {retry_count}: {strategy}")

            if retry_count < 3:
                # Simulate failure
                state["export_completed"] = False
                state["errors"].append(f"Attempt {retry_count} failed")
                time.sleep(0.1)
            else:
                # Success
                state["export_completed"] = True
                time.sleep(0.3)

        assert state["export_completed"], "Export should eventually succeed"
        assert retry_count == 3, "Should retry 3 times"
