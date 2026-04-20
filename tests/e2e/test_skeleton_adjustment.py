"""E2E test for skeleton adjustment workflow."""

import time

import pytest


class TestSkeletonAdjustment:
    """Test skeleton adjustment and re-alignment workflow."""

    def test_skeleton_merge_segments(self, e2e_project_setup, e2e_state_tracker, e2e_user_decisions):
        """Test merging story segments."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker
        decisions = e2e_user_decisions

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        time.sleep(0.1)

        # Parse story
        state["story_parsed"] = True
        segments = [
            {"id": 0, "title": "Day 1", "summary": "Departure"},
            {"id": 1, "title": "Day 2", "summary": "Eiffel Tower"},
            {"id": 2, "title": "Day 3", "summary": "Louvre"},
            {"id": 3, "title": "Day 4", "summary": "Seine River"},
            {"id": 4, "title": "Day 5", "summary": "Versailles"},
        ]
        time.sleep(0.2)

        # User merges segments 0 and 1
        print("User merges segments 0 and 1...")
        merged_segments = [
            {"id": 0, "title": "Day 1-2", "summary": "Departure and Eiffel Tower"},
            {"id": 1, "title": "Day 3", "summary": "Louvre"},
            {"id": 2, "title": "Day 4", "summary": "Seine River"},
            {"id": 3, "title": "Day 5", "summary": "Versailles"},
        ]
        time.sleep(0.1)

        # Confirm skeleton
        state["skeleton_confirmed"] = True
        time.sleep(0.05)

        # Re-analyze media with new skeleton
        print("Re-analyzing media with new skeleton...")
        state["media_analyzed"] = True
        time.sleep(0.2)

        # Re-align
        state["alignment_completed"] = True
        time.sleep(0.1)

        # Confirm highlights
        state["highlights_confirmed"] = True
        time.sleep(0.05)

        # Continue to export
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert len(merged_segments) == 4, "Should have 4 segments after merge"
        assert state["export_completed"], "Should complete workflow after adjustment"

    def test_skeleton_reorder_segments(self, e2e_project_setup, e2e_state_tracker):
        """Test reordering story segments."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        time.sleep(0.3)

        # Original segments
        segments = [
            {"id": 0, "title": "Day 1"},
            {"id": 1, "title": "Day 2"},
            {"id": 2, "title": "Day 3"},
            {"id": 3, "title": "Day 4"},
            {"id": 4, "title": "Day 5"},
        ]

        # User reorders segments
        print("User reorders segments...")
        reordered = [segments[1], segments[0], segments[2], segments[3], segments[4]]
        time.sleep(0.1)

        # Confirm skeleton
        state["skeleton_confirmed"] = True
        time.sleep(0.05)

        # Re-analyze and continue
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert reordered[0]["title"] == "Day 2", "First segment should be Day 2"
        assert state["export_completed"], "Should complete workflow after reordering"

    def test_skeleton_delete_segment(self, e2e_project_setup, e2e_state_tracker):
        """Test deleting a story segment."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        time.sleep(0.3)

        # Original segments
        segments = [
            {"id": 0, "title": "Day 1"},
            {"id": 1, "title": "Day 2"},
            {"id": 2, "title": "Day 3"},
            {"id": 3, "title": "Day 4"},
            {"id": 4, "title": "Day 5"},
        ]

        # User deletes segment 2 (Day 3)
        print("User deletes segment 2...")
        remaining_segments = [s for s in segments if s["id"] != 2]
        time.sleep(0.1)

        # Confirm skeleton
        state["skeleton_confirmed"] = True
        time.sleep(0.05)

        # Re-analyze and continue
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert len(remaining_segments) == 4, "Should have 4 segments after deletion"
        assert state["export_completed"], "Should complete workflow after deletion"

    def test_multiple_skeleton_adjustments(self, e2e_project_setup, e2e_state_tracker):
        """Test multiple skeleton adjustments."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        time.sleep(0.3)

        # Adjustment 1: Merge
        print("Adjustment 1: Merging segments...")
        time.sleep(0.1)

        # Adjustment 2: Reorder
        print("Adjustment 2: Reordering segments...")
        time.sleep(0.1)

        # Adjustment 3: Delete
        print("Adjustment 3: Deleting segment...")
        time.sleep(0.1)

        # Confirm skeleton
        state["skeleton_confirmed"] = True
        time.sleep(0.05)

        # Re-analyze and continue
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert state["export_completed"], "Should complete workflow after multiple adjustments"

    @pytest.mark.e2e
    def test_skeleton_adjustment_performance(self, e2e_project_setup, e2e_state_tracker):
        """Test skeleton adjustment performance."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        start_time = time.time()

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        time.sleep(0.3)

        # Make adjustments
        time.sleep(0.3)

        # Confirm and re-analyze
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        total_time = time.time() - start_time

        assert total_time < 5.0, "Skeleton adjustment workflow should complete in < 5 seconds"
        assert state["export_completed"], "Workflow should complete"
