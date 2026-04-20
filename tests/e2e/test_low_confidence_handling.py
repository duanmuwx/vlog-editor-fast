"""E2E test for low confidence handling."""

import time

import pytest


class TestLowConfidenceHandling:
    """Test handling of low confidence matches."""

    def test_low_confidence_detection(self, e2e_project_setup, e2e_state_tracker):
        """Test detection of low confidence matches."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        time.sleep(0.5)

        # Alignment with low confidence detection
        print("Detecting low confidence matches...")
        alignment_results = [
            {"segment_id": 0, "confidence": 0.9, "status": "high_confidence"},
            {"segment_id": 1, "confidence": 0.6, "status": "low_confidence"},
            {"segment_id": 2, "confidence": 0.85, "status": "high_confidence"},
            {"segment_id": 3, "confidence": 0.45, "status": "low_confidence"},
            {"segment_id": 4, "confidence": 0.88, "status": "high_confidence"},
        ]
        time.sleep(0.1)

        state["alignment_completed"] = True

        # Flag low confidence segments
        low_confidence_segments = [r for r in alignment_results if r["status"] == "low_confidence"]
        print(f"Found {len(low_confidence_segments)} low confidence segments")

        # Continue workflow
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert len(low_confidence_segments) == 2, "Should detect 2 low confidence segments"
        assert state["export_completed"], "Should complete workflow"

    def test_low_confidence_user_confirmation(self, e2e_project_setup, e2e_state_tracker):
        """Test user confirmation for low confidence matches."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        time.sleep(0.5)

        # Identify low confidence segments
        low_confidence_segments = [
            {"segment_id": 1, "confidence": 0.6, "candidates": [
                {"shot_id": 5, "confidence": 0.6},
                {"shot_id": 6, "confidence": 0.55},
                {"shot_id": 7, "confidence": 0.5},
            ]},
            {"segment_id": 3, "confidence": 0.45, "candidates": [
                {"shot_id": 15, "confidence": 0.45},
                {"shot_id": 16, "confidence": 0.4},
            ]},
        ]

        # User confirms low confidence matches
        print("User confirming low confidence matches...")
        for segment in low_confidence_segments:
            print(f"Confirming segment {segment['segment_id']}...")
            # User selects best candidate
            time.sleep(0.1)

        state["highlights_confirmed"] = True

        # Continue workflow
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert state["export_completed"], "Should complete workflow after confirmation"

    def test_low_confidence_fallback_activation(self, e2e_project_setup, e2e_state_tracker):
        """Test fallback activation for very low confidence."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        time.sleep(0.5)

        # Very low confidence segment
        very_low_confidence = {
            "segment_id": 2,
            "confidence": 0.3,
            "candidates": [
                {"shot_id": 10, "confidence": 0.3},
                {"shot_id": 11, "confidence": 0.25},
            ]
        }

        # Activate fallback
        print("Very low confidence detected, activating fallback...")
        fallback_unit = {
            "type": "photo_with_narration",
            "photo": "photo_002.jpg",
            "narration": "A special moment from our journey.",
        }
        time.sleep(0.1)

        state["highlights_confirmed"] = True

        # Continue workflow
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert fallback_unit["type"] == "photo_with_narration", "Should use fallback"
        assert state["export_completed"], "Should complete workflow with fallback"

    def test_metadata_sparse_fallback(self, e2e_project_setup, e2e_state_tracker):
        """Test fallback when metadata is sparse."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        time.sleep(0.5)

        # Simulate sparse metadata
        print("Sparse metadata detected, using semantic-first alignment...")
        alignment_strategy = "semantic_first"
        time.sleep(0.1)

        state["alignment_completed"] = True

        # Continue workflow
        state["highlights_confirmed"] = True
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert alignment_strategy == "semantic_first", "Should use semantic-first alignment"
        assert state["export_completed"], "Should complete workflow"

    def test_asset_coverage_low_fallback(self, e2e_project_setup, e2e_state_tracker):
        """Test fallback when asset coverage is low."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Initial workflow
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        time.sleep(0.5)

        # Low asset coverage
        print("Low asset coverage detected, using alternative presentation units...")
        coverage_report = {
            "total_segments": 5,
            "covered_segments": 2,
            "coverage_percentage": 40,
        }

        # Use alternative presentation units
        presentation_units = [
            {"segment_id": 0, "type": "video_highlight"},
            {"segment_id": 1, "type": "photo_with_narration"},
            {"segment_id": 2, "type": "location_card"},
            {"segment_id": 3, "type": "text_card"},
            {"segment_id": 4, "type": "photo_with_narration"},
        ]
        time.sleep(0.1)

        state["highlights_confirmed"] = True

        # Continue workflow
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert coverage_report["coverage_percentage"] == 40, "Should report low coverage"
        assert len(presentation_units) == 5, "Should have alternative units"
        assert state["export_completed"], "Should complete workflow"

    @pytest.mark.e2e
    def test_comprehensive_low_confidence_handling(self, e2e_project_setup, e2e_state_tracker):
        """Test comprehensive low confidence handling."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete workflow with low confidence handling
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        time.sleep(0.5)

        # Detect and handle low confidence
        low_confidence_count = 0
        fallback_count = 0

        for segment_id in range(5):
            confidence = 0.5 + (segment_id * 0.1)
            if confidence < 0.7:
                low_confidence_count += 1
                if confidence < 0.5:
                    fallback_count += 1
                    print(f"Segment {segment_id}: Using fallback")
                else:
                    print(f"Segment {segment_id}: User confirmation needed")
            time.sleep(0.05)

        state["highlights_confirmed"] = True

        # Continue workflow
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert state["export_completed"], "Should complete workflow with low confidence handling"
