"""Integration tests for Phase 4 flow."""

import pytest
import tempfile
import os
from pathlib import Path

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.story_parser import StoryParser
from src.server.modules.skeleton_confirmation import SkeletonConfirmation
from src.server.modules.media_analyzer import MediaAnalyzer
from src.server.modules.alignment_engine import AlignmentEngine
from src.server.modules.highlight_confirmation import HighlightConfirmation
from src.server.modules.run_orchestrator import RunOrchestrator
from src.server.modules.diagnostic_reporter import DiagnosticReporter


@pytest.fixture
def temp_project_media():
    """Create temporary project with media files."""
    temp_dir = tempfile.mkdtemp()

    video_files = []
    for i in range(3):
        video_path = os.path.join(temp_dir, f"video_{i}.mp4")
        Path(video_path).write_bytes(b"dummy video content")
        video_files.append(video_path)

    photo_files = []
    for i in range(20):
        photo_path = os.path.join(temp_dir, f"photo_{i}.jpg")
        Path(photo_path).write_bytes(b"dummy photo content")
        photo_files.append(photo_path)

    # Create BGM file
    bgm_path = os.path.join(temp_dir, "bgm.mp3")
    Path(bgm_path).write_bytes(b"dummy bgm")

    yield {
        "temp_dir": temp_dir,
        "videos": video_files,
        "photos": photo_files,
        "all_files": video_files + photo_files,
        "bgm_path": bgm_path
    }

    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_complete_phase4_flow(temp_project_media):
    """Test complete Phase 4 flow: edit plan → narration → audio → render."""
    media_files = temp_project_media["all_files"]
    bgm_path = temp_project_media["bgm_path"]

    input_contract = ProjectInputContract(
        project_name="Phase 4 Test Project",
        travel_note="这是第一天的故事。我们到达了北京。" * 20
                    + "这是第二天的故事。我们参观了长城。" * 20
                    + "这是第三天的故事。我们游览了故宫。" * 20,
        media_files=media_files,
        bgm_asset=bgm_path,
        tts_voice="default"
    )

    project_id = ProjectManager.create_project(input_contract)
    assert project_id is not None

    config = ProjectManager.get_project_config(project_id)
    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    assert skeleton.total_segments >= 3

    confirmed_skeleton = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])
    assert confirmed_skeleton.status == "confirmed"

    analysis = MediaAnalyzer.analyze_media(project_id)
    assert analysis.total_shots >= 0
    assert analysis.analysis_status in ["completed", "partial", "degraded"]

    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)
    assert len(candidates) > 0

    selections = []
    for segment in confirmed_skeleton.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        confirmed_highlights = HighlightConfirmation.confirm_highlights(
            project_id, skeleton.skeleton_id, selections
        )
        assert len(confirmed_highlights) == len(selections)
        assert all(h.user_confirmed for h in confirmed_highlights)

    # Phase 4: Run complete pipeline
    export_bundle = RunOrchestrator.run_phase4(project_id, bgm_path, "default")

    assert export_bundle.export_id is not None
    assert export_bundle.status == "success"
    assert os.path.exists(export_bundle.video_path)
    assert os.path.exists(export_bundle.subtitle_path)
    assert os.path.exists(export_bundle.manifest_path)


def test_phase4_with_regeneration(temp_project_media):
    """Test Phase 4 with local regeneration."""
    media_files = temp_project_media["all_files"]
    bgm_path = temp_project_media["bgm_path"]

    input_contract = ProjectInputContract(
        project_name="Phase 4 Regeneration Test",
        travel_note="这是第一段。" * 15 + "这是第二段。" * 15 + "这是第三段。" * 15,
        media_files=media_files,
        bgm_asset=bgm_path,
        tts_voice="default"
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    MediaAnalyzer.analyze_media(project_id)
    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)

    selections = []
    for segment in confirmed.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        HighlightConfirmation.confirm_highlights(project_id, skeleton.skeleton_id, selections)

    # Initial export
    export_bundle_1 = RunOrchestrator.run_phase4(project_id, bgm_path, "default")
    assert export_bundle_1.status == "success"

    # Regenerate narration only
    export_bundle_2 = RunOrchestrator.regenerate_narration(project_id, "default")
    assert export_bundle_2.status == "success"
    assert export_bundle_2.export_id != export_bundle_1.export_id

    # Regenerate audio only
    export_bundle_3 = RunOrchestrator.regenerate_audio(project_id, bgm_path)
    assert export_bundle_3.status == "success"
    assert export_bundle_3.export_id != export_bundle_2.export_id

    # Regenerate shorter
    export_bundle_4 = RunOrchestrator.regenerate_shorter(project_id, 120.0)
    assert export_bundle_4.status == "success"
    assert export_bundle_4.export_id != export_bundle_3.export_id


def test_phase4_diagnostics(temp_project_media):
    """Test Phase 4 diagnostics reporting."""
    media_files = temp_project_media["all_files"]
    bgm_path = temp_project_media["bgm_path"]

    input_contract = ProjectInputContract(
        project_name="Phase 4 Diagnostics Test",
        travel_note="这是第一段。" * 15 + "这是第二段。" * 15 + "这是第三段。" * 15,
        media_files=media_files,
        bgm_asset=bgm_path,
        tts_voice="default"
    )

    project_id = ProjectManager.create_project(input_contract)
    config = ProjectManager.get_project_config(project_id)

    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])

    MediaAnalyzer.analyze_media(project_id)
    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)

    selections = []
    for segment in confirmed.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        HighlightConfirmation.confirm_highlights(project_id, skeleton.skeleton_id, selections)

    # Run Phase 4
    export_bundle = RunOrchestrator.run_phase4(project_id, bgm_path, "default")

    # Get diagnostics
    from src.server.storage.database import get_or_create_db
    from src.server.storage.schemas import RunRecord
    db = get_or_create_db(project_id)
    session = db.get_session()
    try:
        run_record = session.query(RunRecord).filter_by(
            project_id=project_id
        ).order_by(RunRecord.started_at.desc()).first()

        if run_record:
            diagnostics = DiagnosticReporter.report_diagnostics(project_id, run_record.run_id)
            assert diagnostics is not None
            assert "run_id" in diagnostics
            assert "status" in diagnostics
    finally:
        session.close()


def test_phase4_end_to_end_with_all_phases(temp_project_media):
    """Test complete end-to-end workflow from Phase 1 to Phase 4."""
    media_files = temp_project_media["all_files"]
    bgm_path = temp_project_media["bgm_path"]

    # Phase 1: Create project
    input_contract = ProjectInputContract(
        project_name="End-to-End Test",
        travel_note="这是第一天的故事。我们到达了北京。" * 20
                    + "这是第二天的故事。我们参观了长城。" * 20
                    + "这是第三天的故事。我们游览了故宫。" * 20,
        media_files=media_files,
        bgm_asset=bgm_path,
        tts_voice="default"
    )

    project_id = ProjectManager.create_project(input_contract)
    assert project_id is not None

    # Phase 2: Parse story and confirm skeleton
    config = ProjectManager.get_project_config(project_id)
    skeleton = StoryParser.parse_story(project_id, config.travel_note)
    confirmed_skeleton = SkeletonConfirmation.confirm_skeleton(project_id, skeleton.skeleton_id, [])
    assert confirmed_skeleton.status == "confirmed"

    # Phase 3: Analyze media, align, and confirm highlights
    analysis = MediaAnalyzer.analyze_media(project_id)
    assert analysis.total_shots >= 0

    candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)
    assert len(candidates) > 0

    selections = []
    for segment in confirmed_skeleton.segments:
        segment_candidates = [c for c in candidates if c.segment_id == segment.segment_id]
        if segment_candidates:
            selections.append({
                "segment_id": segment.segment_id,
                "shot_id": segment_candidates[0].shot_id,
                "user_confirmed": True
            })

    if selections:
        confirmed_highlights = HighlightConfirmation.confirm_highlights(
            project_id, skeleton.skeleton_id, selections
        )
        assert len(confirmed_highlights) == len(selections)

    # Phase 4: Generate final vlog
    export_bundle = RunOrchestrator.run_phase4(project_id, bgm_path, "default")

    assert export_bundle.export_id is not None
    assert export_bundle.status == "success"
    assert os.path.exists(export_bundle.video_path)
    assert os.path.exists(export_bundle.subtitle_path)
    assert os.path.exists(export_bundle.manifest_path)

    # Verify final project status
    final_status = ProjectManager.get_project_metadata(project_id)
    assert final_status.status == "exported"
