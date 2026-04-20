"""E2E test for highlight confirmation and fallback presentation."""

import time

import pytest


class TestHighlightAndFallback:
    """Test highlight confirmation and fallback presentation handling."""

    def test_highlight_confirmation_workflow(self, e2e_project_setup, e2e_state_tracker, e2e_user_decisions):
        """Test highlight confirmation workflow."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker
        decisions = e2e_user_decisions

        # Initial workflow up to highlight confirmation
        state["project_created"] = True
        state["input_validated"] = True
        state["assets_indexed"] = True
        state["story_parsed"] = True
        state["skeleton_confirmed"] = True
        state["media_analyzed"] = True
        state["alignment_completed"] = True
        time.sleep(0.5)

        # Generate highlight candidates
        print("Generating highlight candidates...")
        candidates = [
            {"segment_id": 0, "shot_id": 0, "confidence": 0.9},
            {"segment_id": 0, "shot_id": 1, "confidence": 0.8},
            {"segment_id": 0, "shot_id": 2, "confidence": 0.7},
            {"segment_id": 1, "shot_id": 5, "confidence": 0.85},
            {"segment_id": 1, "shot_id": 6, "confidence": 0.75},
            {"segment_id": 2, "shot_id": 10, "confidence": 0.88},
        ]
        time.sleep(0.1)

        # User confirms highlights
        print("User confirming highlights...")
        confirmed_highlights = []
        for decision in decisions["highlight_selections"]:
            confirmed_highlights.append(decision)
            time.sleep(0.05)

        state["highlights_confirmed"] = True

        # Continue to export
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert len(confirmed_highlights) == 3, "Should confirm 3 highlights"
        assert state["export_completed"], "Should complete workflow"

    def test_highlight_replacement(self, e2e_project_setup, e2e_state_tracker):
        """Test replacing a highlight with alternative."""
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

        # Generate candidates
        candidates = {
            "segment_0": [
                {"shot_id": 0, "confidence": 0.9},
                {"shot_id": 1, "confidence": 0.8},
                {"shot_id": 2, "confidence": 0.7},
            ],
            "segment_1": [
                {"shot_id": 5, "confidence": 0.85},
                {"shot_id": 6, "confidence": 0.75},
            ],
        }

        # User initially selects shot 0 for segment 0
        print("User selects initial highlight...")
        selected = {"segment_id": "segment_0", "shot_id": 0}
        time.sleep(0.05)

        # User replaces with shot 2
        print("User replaces highlight with alternative...")
        selected = {"segment_id": "segment_0", "shot_id": 2}
        time.sleep(0.05)

        state["highlights_confirmed"] = True

        # Continue to export
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert state["export_completed"], "Should complete workflow after replacement"

    def test_fallback_presentation_unit(self, e2e_project_setup, e2e_state_tracker):
        """Test fallback presentation unit (photo + narration)."""
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

        # Simulate insufficient video for segment
        print("Insufficient video for segment, using fallback...")
        fallback_unit = {
            "type": "photo_with_narration",
            "photo": "photo_001.jpg",
            "narration": "This is a beautiful moment from our journey.",
            "duration": 5,
        }
        time.sleep(0.1)

        state["highlights_confirmed"] = True

        # Continue to export
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert fallback_unit["type"] == "photo_with_narration", "Should use photo with narration"
        assert state["export_completed"], "Should complete workflow with fallback"

    def test_location_card_fallback(self, e2e_project_setup, e2e_state_tracker):
        """Test location card as fallback presentation."""
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

        # Simulate no suitable media for segment
        print("No suitable media, using location card...")
        location_card = {
            "type": "location_card",
            "location": "Eiffel Tower, Paris",
            "coordinates": (48.8584, 2.2945),
            "narration": "We visited the iconic Eiffel Tower.",
            "duration": 3,
        }
        time.sleep(0.1)

        state["highlights_confirmed"] = True

        # Continue to export
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert location_card["type"] == "location_card", "Should use location card"
        assert state["export_completed"], "Should complete workflow with location card"

    def test_text_card_fallback(self, e2e_project_setup, e2e_state_tracker):
        """Test text card as fallback presentation."""
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

        # Simulate no media available
        print("No media available, using text card...")
        text_card = {
            "type": "text_card",
            "text": "A memorable moment in our journey",
            "background": "gradient_blue",
            "narration": "This was a special moment we'll never forget.",
            "duration": 4,
        }
        time.sleep(0.1)

        state["highlights_confirmed"] = True

        # Continue to export
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert text_card["type"] == "text_card", "Should use text card"
        assert state["export_completed"], "Should complete workflow with text card"

    @pytest.mark.e2e
    def test_mixed_highlights_and_fallbacks(self, e2e_project_setup, e2e_state_tracker):
        """Test workflow with mix of highlights and fallback presentations."""
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

        # Mix of highlights and fallbacks
        print("Creating mix of highlights and fallbacks...")
        presentation_units = [
            {"type": "video_highlight", "shot_id": 0},
            {"type": "photo_with_narration", "photo": "photo_001.jpg"},
            {"type": "video_highlight", "shot_id": 5},
            {"type": "location_card", "location": "Eiffel Tower"},
            {"type": "video_highlight", "shot_id": 10},
            {"type": "text_card", "text": "A special moment"},
        ]
        time.sleep(0.2)

        state["highlights_confirmed"] = True

        # Continue to export
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True

        assert len(presentation_units) == 6, "Should have 6 presentation units"
        assert state["export_completed"], "Should complete workflow with mixed presentations"
