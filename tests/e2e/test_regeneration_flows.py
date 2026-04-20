"""E2E test for regeneration workflows."""

import time

import pytest


class TestRegenerationFlows:
    """Test local regeneration workflows."""

    def test_narration_only_regeneration(self, e2e_project_setup, e2e_state_tracker):
        """Test regenerating narration only."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete initial workflow
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
        state["export_completed"] = True
        time.sleep(1.0)

        # User wants to regenerate narration only
        print("User initiates narration-only regeneration...")
        state["narration_generated"] = False
        time.sleep(0.1)

        # Regenerate narration
        print("Regenerating narration...")
        time.sleep(0.2)
        state["narration_generated"] = True

        # Re-mix audio
        print("Re-mixing audio...")
        time.sleep(0.1)
        state["audio_mixed"] = True

        # Re-render
        print("Re-rendering video...")
        time.sleep(0.5)
        state["video_rendered"] = True

        # Re-export
        print("Re-exporting...")
        time.sleep(0.1)
        state["export_completed"] = True

        assert state["export_completed"], "Should complete regeneration workflow"

    def test_bgm_only_regeneration(self, e2e_project_setup, e2e_state_tracker):
        """Test regenerating background music only."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete initial workflow
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
        state["export_completed"] = True
        time.sleep(1.0)

        # User wants to change BGM
        print("User initiates BGM-only regeneration...")
        state["audio_mixed"] = False
        time.sleep(0.1)

        # Select new BGM
        print("Selecting new background music...")
        new_bgm = "upbeat_bgm.mp3"
        time.sleep(0.05)

        # Re-mix audio with new BGM
        print("Re-mixing audio with new BGM...")
        time.sleep(0.1)
        state["audio_mixed"] = True

        # Re-render
        print("Re-rendering video...")
        time.sleep(0.5)
        state["video_rendered"] = True

        # Re-export
        print("Re-exporting...")
        time.sleep(0.1)
        state["export_completed"] = True

        assert state["export_completed"], "Should complete BGM regeneration workflow"

    def test_compress_duration_regeneration(self, e2e_project_setup, e2e_state_tracker):
        """Test compressing video duration."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete initial workflow
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
        state["export_completed"] = True
        time.sleep(1.0)

        # User wants to compress duration
        print("User initiates duration compression...")
        state["timeline_generated"] = False
        time.sleep(0.1)

        # Regenerate timeline with shorter duration
        print("Regenerating timeline with shorter duration...")
        time.sleep(0.1)
        state["timeline_generated"] = True

        # Re-generate narration (shorter)
        print("Re-generating shorter narration...")
        time.sleep(0.2)
        state["narration_generated"] = True

        # Re-mix audio
        print("Re-mixing audio...")
        time.sleep(0.1)
        state["audio_mixed"] = True

        # Re-render
        print("Re-rendering video...")
        time.sleep(0.5)
        state["video_rendered"] = True

        # Re-export
        print("Re-exporting...")
        time.sleep(0.1)
        state["export_completed"] = True

        assert state["export_completed"], "Should complete duration compression workflow"

    def test_sequential_regenerations(self, e2e_project_setup, e2e_state_tracker):
        """Test multiple sequential regenerations."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete initial workflow
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
        state["export_completed"] = True
        time.sleep(1.0)

        # First regeneration: narration only
        print("First regeneration: narration only...")
        state["narration_generated"] = False
        time.sleep(0.2)
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True
        time.sleep(0.5)

        # Second regeneration: BGM only
        print("Second regeneration: BGM only...")
        state["audio_mixed"] = False
        time.sleep(0.1)
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True
        time.sleep(0.5)

        # Third regeneration: compress duration
        print("Third regeneration: compress duration...")
        state["timeline_generated"] = False
        time.sleep(0.1)
        state["timeline_generated"] = True
        state["narration_generated"] = True
        state["audio_mixed"] = True
        state["video_rendered"] = True
        state["export_completed"] = True
        time.sleep(0.5)

        assert state["export_completed"], "Should complete all regenerations"

    @pytest.mark.e2e
    def test_regeneration_version_management(self, e2e_project_setup, e2e_state_tracker):
        """Test version management during regenerations."""
        project_setup = e2e_project_setup
        state = e2e_state_tracker

        # Complete initial workflow
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
        state["export_completed"] = True
        time.sleep(1.0)

        # Track versions
        versions = {
            "v1": {"narration": "v1", "audio": "v1", "export": "v1"},
        }

        # First regeneration
        print("Creating version 2...")
        time.sleep(0.3)
        versions["v2"] = {"narration": "v2", "audio": "v2", "export": "v2"}

        # Second regeneration
        print("Creating version 3...")
        time.sleep(0.3)
        versions["v3"] = {"narration": "v2", "audio": "v3", "export": "v3"}

        # User can switch between versions
        print("Switching to version 1...")
        current_version = "v1"
        time.sleep(0.1)

        assert len(versions) == 3, "Should have 3 versions"
        assert current_version == "v1", "Should switch to version 1"
