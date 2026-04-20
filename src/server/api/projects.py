"""Project API routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Response

from src.shared.types import ProjectInputContract, SkeletonConfirmationRequest
from src.server.modules.project_manager import ProjectManager
from src.server.modules.input_validator import InputValidator
from src.server.modules.asset_indexer import AssetIndexer
from src.server.modules.story_parser import StoryParser
from src.server.modules.story_skeleton import StorySkeletonManager
from src.server.modules.skeleton_confirmation import SkeletonConfirmation
from src.server.modules.media_analyzer import MediaAnalyzer
from src.server.modules.alignment_engine import AlignmentEngine
from src.server.modules.highlight_confirmation import HighlightConfirmation
from src.server.modules.edit_planner import EditPlanner
from src.server.modules.narration_engine import NarrationEngine
from src.server.modules.audio_composer import AudioComposer
from src.server.modules.renderer import Renderer
from src.server.modules.run_orchestrator import RunOrchestrator
from src.server.modules.diagnostic_reporter import DiagnosticReporter

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _parse_resolution(resolution: Optional[str]) -> Optional[List[int]]:
    """Convert database resolution strings to JSON-friendly arrays."""
    if not resolution:
        return None

    try:
        width, height = resolution.lower().split("x", maxsplit=1)
        return [int(width), int(height)]
    except (AttributeError, ValueError):
        return None


@router.get("")
async def list_projects():
    """List all projects."""
    try:
        projects = ProjectManager.list_projects()
        return {
            "total_projects": len(projects),
            "projects": [project.dict() for project in projects],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create")
async def create_project(input_contract: ProjectInputContract):
    """Create a new project."""
    try:
        # Create project
        project_id = ProjectManager.create_project(input_contract)

        # Validate input
        validation_report = InputValidator.validate(project_id, input_contract)

        # Index assets
        asset_index = AssetIndexer.index_assets(project_id, input_contract.media_files)

        # Update project status
        if validation_report.is_valid:
            ProjectManager.update_project_status(project_id, "ready")
        else:
            ProjectManager.update_project_status(project_id, "draft")

        return {
            "project_id": project_id,
            "validation_report": validation_report.dict(),
            "asset_index": asset_index.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get project information."""
    try:
        metadata = ProjectManager.get_project_metadata(project_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Project not found")

        config = ProjectManager.get_project_config(project_id)

        return {
            "metadata": metadata.dict(),
            "config": config.dict() if config else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str):
    """Delete a project and its workspace."""
    try:
        deleted = ProjectManager.delete_project(project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")

        return Response(status_code=204)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/validate")
async def validate_project(project_id: str):
    """Validate project input."""
    try:
        input_contract = ProjectManager.get_project_input_contract(project_id)
        if not input_contract:
            raise HTTPException(status_code=404, detail="Project not found")

        validation_report = InputValidator.validate(project_id, input_contract)

        return {"validation_report": validation_report.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/assets")
async def get_assets(project_id: str):
    """Get asset index."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import AssetIndexRecord, MediaFileRecord

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            index_record = session.query(AssetIndexRecord).filter(
                AssetIndexRecord.project_id == project_id
            ).first()

            if not index_record:
                raise HTTPException(status_code=404, detail="Asset index not found")

            media_items = session.query(MediaFileRecord).filter(
                MediaFileRecord.project_id == project_id
            ).order_by(MediaFileRecord.indexed_at.asc(), MediaFileRecord.file_path.asc()).all()

            return {
                "index_id": index_record.index_id,
                "project_id": index_record.project_id,
                "total_videos": index_record.total_videos,
                "total_photos": index_record.total_photos,
                "total_duration": index_record.total_duration,
                "media_items": [
                    {
                        "file_id": item.file_id,
                        "file_path": item.file_path,
                        "file_type": item.file_type,
                        "file_size": item.file_size,
                        "duration": item.duration,
                        "resolution": _parse_resolution(item.resolution),
                        "creation_time": item.creation_time,
                        "has_audio": item.has_audio,
                        "exif_data": item.exif_data,
                    }
                    for item in media_items
                ],
                "metadata_availability": index_record.metadata_availability,
                "indexed_at": index_record.indexed_at
            }
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/story/parse")
async def parse_story(project_id: str):
    """Parse travel narrative into story segments."""
    try:
        config = ProjectManager.get_project_config(project_id)
        if not config:
            raise HTTPException(status_code=404, detail="Project not found")

        skeleton = StoryParser.parse_story(project_id, config.travel_note)
        ProjectManager.update_project_status(project_id, "story_parsed")

        return {
            "skeleton_id": skeleton.skeleton_id,
            "project_id": skeleton.project_id,
            "version": skeleton.version,
            "total_segments": skeleton.total_segments,
            "narrative_coverage": skeleton.narrative_coverage,
            "parsing_confidence": skeleton.parsing_confidence,
            "status": skeleton.status,
            "segments": [seg.dict() for seg in skeleton.segments],
            "created_at": skeleton.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/skeleton/{skeleton_id}")
async def get_skeleton(project_id: str, skeleton_id: str):
    """Retrieve story skeleton."""
    try:
        skeleton = StorySkeletonManager.get_skeleton(project_id, skeleton_id)
        if not skeleton:
            raise HTTPException(status_code=404, detail="Skeleton not found")

        return {
            "skeleton_id": skeleton.skeleton_id,
            "project_id": skeleton.project_id,
            "version": skeleton.version,
            "total_segments": skeleton.total_segments,
            "narrative_coverage": skeleton.narrative_coverage,
            "parsing_confidence": skeleton.parsing_confidence,
            "status": skeleton.status,
            "segments": [seg.dict() for seg in skeleton.segments],
            "created_at": skeleton.created_at,
            "confirmed_at": skeleton.confirmed_at,
            "user_edits": skeleton.user_edits
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/skeleton/{skeleton_id}/confirm")
async def confirm_skeleton(project_id: str, skeleton_id: str, request: SkeletonConfirmationRequest):
    """Confirm skeleton with user edits."""
    try:
        confirmed_skeleton = SkeletonConfirmation.confirm_skeleton(
            project_id, skeleton_id, request.edits
        )
        ProjectManager.update_project_status(project_id, "skeleton_confirmed")

        return {
            "skeleton_id": confirmed_skeleton.skeleton_id,
            "project_id": confirmed_skeleton.project_id,
            "version": confirmed_skeleton.version,
            "total_segments": confirmed_skeleton.total_segments,
            "narrative_coverage": confirmed_skeleton.narrative_coverage,
            "parsing_confidence": confirmed_skeleton.parsing_confidence,
            "status": confirmed_skeleton.status,
            "segments": [seg.dict() for seg in confirmed_skeleton.segments],
            "created_at": confirmed_skeleton.created_at,
            "confirmed_at": confirmed_skeleton.confirmed_at,
            "user_edits": confirmed_skeleton.user_edits
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/skeleton/current")
async def get_current_skeleton(project_id: str):
    """Get latest confirmed skeleton."""
    try:
        skeleton = StorySkeletonManager.get_current_skeleton(project_id)
        if not skeleton:
            raise HTTPException(status_code=404, detail="No skeleton found for project")

        return {
            "skeleton_id": skeleton.skeleton_id,
            "project_id": skeleton.project_id,
            "version": skeleton.version,
            "total_segments": skeleton.total_segments,
            "narrative_coverage": skeleton.narrative_coverage,
            "parsing_confidence": skeleton.parsing_confidence,
            "status": skeleton.status,
            "segments": [seg.dict() for seg in skeleton.segments],
            "created_at": skeleton.created_at,
            "confirmed_at": skeleton.confirmed_at,
            "user_edits": skeleton.user_edits
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/analyze-media")
async def analyze_media(project_id: str):
    """Analyze media files for shots and quality."""
    try:
        metadata = ProjectManager.get_project_metadata(project_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Project not found")

        analysis = MediaAnalyzer.analyze_media(project_id)
        ProjectManager.update_project_status(project_id, "media_analyzed")

        return {
            "analysis_id": analysis.analysis_id,
            "project_id": analysis.project_id,
            "total_shots": analysis.total_shots,
            "analysis_status": analysis.analysis_status,
            "shots": [shot.dict() for shot in analysis.shots],
            "created_at": analysis.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/media-analysis")
async def get_media_analysis(project_id: str):
    """Retrieve media analysis results."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import MediaAnalysisRecord, MediaShotRecord

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            analysis_record = session.query(MediaAnalysisRecord).filter_by(project_id=project_id).first()

            if not analysis_record:
                raise HTTPException(status_code=404, detail="Media analysis not found")

            shot_records = session.query(MediaShotRecord).filter_by(project_id=project_id).all()

            return {
                "analysis_id": analysis_record.analysis_id,
                "project_id": analysis_record.project_id,
                "total_shots": analysis_record.total_shots,
                "analysis_status": analysis_record.analysis_status,
                "shots": [
                    {
                        "shot_id": s.shot_id,
                        "file_id": s.file_id,
                        "shot_type": s.shot_type,
                        "start_time": s.start_time,
                        "end_time": s.end_time,
                        "duration": s.duration,
                        "quality_score": s.quality_score,
                        "has_audio": s.has_audio,
                        "visual_features": s.visual_features,
                        "confidence": s.confidence,
                    }
                    for s in shot_records
                ],
                "created_at": analysis_record.created_at
            }
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/align-media")
async def align_media(project_id: str):
    """Align story segments to media."""
    try:
        skeleton = StorySkeletonManager.get_current_skeleton(project_id)
        if not skeleton:
            raise HTTPException(status_code=404, detail="No confirmed skeleton found")

        candidates = AlignmentEngine.align_media(project_id, skeleton.skeleton_id)
        ProjectManager.update_project_status(project_id, "media_aligned")

        return {
            "total_candidates": len(candidates),
            "candidates": [cand.dict() for cand in candidates],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/alignment-candidates/{segment_id}")
async def get_alignment_candidates(project_id: str, segment_id: str):
    """Get alignment candidates for a segment."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import AlignmentCandidateRecord

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            candidates = session.query(AlignmentCandidateRecord).filter_by(
                project_id=project_id, segment_id=segment_id
            ).order_by(AlignmentCandidateRecord.match_score.desc()).all()

            if not candidates:
                raise HTTPException(status_code=404, detail="No candidates found for segment")

            return {
                "segment_id": segment_id,
                "total_candidates": len(candidates),
                "candidates": [
                    {
                        "candidate_id": c.candidate_id,
                        "segment_id": c.segment_id,
                        "shot_id": c.shot_id,
                        "match_score": c.match_score,
                        "text_match_score": c.text_match_score,
                        "time_match_score": c.time_match_score,
                        "location_match_score": c.location_match_score,
                        "reasoning": c.reasoning,
                    }
                    for c in candidates
                ]
            }
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/confirm-highlights")
async def confirm_highlights(project_id: str, request: dict):
    """Confirm highlight selections."""
    try:
        skeleton = StorySkeletonManager.get_current_skeleton(project_id)
        if not skeleton:
            raise HTTPException(status_code=404, detail="No confirmed skeleton found")

        selections = request.get("selections", [])
        confirmed = HighlightConfirmation.confirm_highlights(project_id, skeleton.skeleton_id, selections)
        ProjectManager.update_project_status(project_id, "highlights_confirmed")

        return {
            "total_selections": len(confirmed),
            "selections": [sel.dict() for sel in confirmed],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/highlights/current")
async def get_current_highlights(project_id: str):
    """Get current confirmed highlights."""
    try:
        highlights = HighlightConfirmation.get_current_highlights(project_id)
        if not highlights:
            raise HTTPException(status_code=404, detail="No confirmed highlights found")

        return {
            "total_selections": len(highlights),
            "selections": [sel.dict() for sel in highlights],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Phase 4: Final Composition & Export

@router.post("/{project_id}/edit-plan")
async def edit_plan(project_id: str):
    """Generate timeline from confirmed story and highlights."""
    try:
        metadata = ProjectManager.get_project_metadata(project_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Project not found")

        timeline = EditPlanner.plan_edit(project_id)
        ProjectManager.update_project_status(project_id, "edit_planned")

        return {
            "timeline_id": timeline.timeline_id,
            "version_id": timeline.version_id,
            "total_duration_seconds": timeline.total_duration_seconds,
            "target_duration_seconds": timeline.target_duration_seconds,
            "segments": [seg.dict() for seg in timeline.segments],
            "created_at": timeline.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/timeline/{version_id}")
async def get_timeline(project_id: str, version_id: str):
    """Retrieve timeline details."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import TimelineRecord, TimelineSegmentRecord

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=version_id
            ).first()

            if not timeline_record:
                raise HTTPException(status_code=404, detail="Timeline not found")

            segments = session.query(TimelineSegmentRecord).filter_by(
                timeline_id=timeline_record.timeline_id
            ).all()

            return {
                "timeline_id": timeline_record.timeline_id,
                "version_id": timeline_record.version_id,
                "total_duration_seconds": timeline_record.total_duration_seconds,
                "target_duration_seconds": timeline_record.target_duration_seconds,
                "segments_count": len(segments),
                "created_at": timeline_record.created_at
            }
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/generate-narration")
async def generate_narration(project_id: str):
    """Generate narration, subtitles, and text cards."""
    try:
        config = ProjectManager.get_project_config(project_id)
        if not config:
            raise HTTPException(status_code=404, detail="Project not found")

        from src.server.modules.artifact_store import ArtifactStore
        timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
        if not timeline_version:
            raise HTTPException(status_code=404, detail="No timeline found")

        from src.server.storage.schemas import TimelineRecord
        from src.server.storage.database import get_or_create_db
        db = get_or_create_db(project_id)
        session = db.get_session()
        try:
            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()
            timeline_id = timeline_record.timeline_id
        finally:
            session.close()

        tts_voice = config.tts_voice or "default"
        narration = NarrationEngine.generate_narration(project_id, timeline_id, tts_voice)
        ProjectManager.update_project_status(project_id, "narration_generated")

        return {
            "narration_id": narration.narration_id,
            "version_id": narration.version_id,
            "narration_text": narration.narration_text,
            "tts_voice": narration.tts_voice,
            "subtitles_count": len(narration.subtitles),
            "text_cards_count": len(narration.text_cards),
            "created_at": narration.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/mix-audio")
async def mix_audio(project_id: str):
    """Mix narration, ambient sound, and BGM."""
    try:
        config = ProjectManager.get_project_config(project_id)
        if not config:
            raise HTTPException(status_code=404, detail="Project not found")

        from src.server.modules.artifact_store import ArtifactStore
        timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
        narration_version = ArtifactStore.get_active_version(project_id, "narration")

        if not timeline_version or not narration_version:
            raise HTTPException(status_code=404, detail="Missing timeline or narration")

        from src.server.storage.schemas import TimelineRecord, NarrationRecord
        from src.server.storage.database import get_or_create_db
        db = get_or_create_db(project_id)
        session = db.get_session()
        try:
            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()
            narration_record = session.query(NarrationRecord).filter_by(
                version_id=narration_version.version_id
            ).first()
            timeline_id = timeline_record.timeline_id
            narration_id = narration_record.narration_id
        finally:
            session.close()

        bgm_asset = config.bgm_asset
        audio_mix = AudioComposer.compose_audio(project_id, timeline_id, narration_id, bgm_asset)
        ProjectManager.update_project_status(project_id, "audio_mixed")

        return {
            "audio_mix_id": audio_mix.audio_mix_id,
            "version_id": audio_mix.version_id,
            "total_duration_seconds": audio_mix.total_duration_seconds,
            "tracks_count": len(audio_mix.tracks),
            "created_at": audio_mix.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/render-export")
async def render_export(project_id: str):
    """Render final video and export."""
    try:
        config = ProjectManager.get_project_config(project_id)
        if not config:
            raise HTTPException(status_code=404, detail="Project not found")

        from src.server.modules.artifact_store import ArtifactStore
        timeline_version = ArtifactStore.get_active_version(project_id, "timeline")
        audio_mix_version = ArtifactStore.get_active_version(project_id, "audio_mix")
        narration_version = ArtifactStore.get_active_version(project_id, "narration")

        if not all([timeline_version, audio_mix_version, narration_version]):
            raise HTTPException(status_code=404, detail="Missing required artifacts")

        from src.server.storage.schemas import TimelineRecord, AudioMixRecord, NarrationRecord
        from src.server.storage.database import get_or_create_db
        db = get_or_create_db(project_id)
        session = db.get_session()
        try:
            timeline_record = session.query(TimelineRecord).filter_by(
                version_id=timeline_version.version_id
            ).first()
            audio_mix_record = session.query(AudioMixRecord).filter_by(
                version_id=audio_mix_version.version_id
            ).first()
            narration_record = session.query(NarrationRecord).filter_by(
                version_id=narration_version.version_id
            ).first()
            timeline_id = timeline_record.timeline_id
            audio_mix_id = audio_mix_record.audio_mix_id
            narration_id = narration_record.narration_id
        finally:
            session.close()

        export_bundle = Renderer.render_export(project_id, timeline_id, audio_mix_id, narration_id)
        ProjectManager.update_project_status(project_id, "exported")

        return {
            "export_id": export_bundle.export_id,
            "version_id": export_bundle.version_id,
            "video_path": export_bundle.video_path,
            "subtitle_path": export_bundle.subtitle_path,
            "narration_path": export_bundle.narration_path,
            "manifest_path": export_bundle.manifest_path,
            "status": export_bundle.status,
            "created_at": export_bundle.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/exports")
async def get_exports(project_id: str):
    """Retrieve all exports."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import ExportRecord

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            exports = session.query(ExportRecord).filter_by(
                project_id=project_id
            ).order_by(ExportRecord.created_at.desc()).all()

            return {
                "total_exports": len(exports),
                "exports": [
                    {
                        "export_id": e.export_id,
                        "version_id": e.version_id,
                        "video_path": e.video_path,
                        "status": e.status,
                        "created_at": e.created_at
                    }
                    for e in exports
                ]
            }
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/diagnostics/{run_id}")
async def get_diagnostics(project_id: str, run_id: str):
    """Retrieve diagnostics for run."""
    try:
        diagnostics = DiagnosticReporter.report_diagnostics(project_id, run_id)
        return diagnostics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/regenerate/{regen_type}")
async def regenerate(project_id: str, regen_type: str, request: dict = None):
    """Regenerate specific component."""
    try:
        config = ProjectManager.get_project_config(project_id)
        if not config:
            raise HTTPException(status_code=404, detail="Project not found")

        if regen_type == "narration":
            tts_voice = config.tts_voice or "default"
            export_bundle = RunOrchestrator.regenerate_narration(project_id, tts_voice)
        elif regen_type == "audio":
            bgm_asset = config.bgm_asset
            export_bundle = RunOrchestrator.regenerate_audio(project_id, bgm_asset)
        elif regen_type == "shorter":
            target_seconds = request.get("target_seconds", 180.0) if request else 180.0
            export_bundle = RunOrchestrator.regenerate_shorter(project_id, target_seconds)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown regeneration type: {regen_type}")

        return {
            "export_id": export_bundle.export_id,
            "version_id": export_bundle.version_id,
            "video_path": export_bundle.video_path,
            "status": export_bundle.status,
            "created_at": export_bundle.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Phase 5: Version Management & Recovery

@router.get("/{project_id}/versions/{artifact_type}")
async def get_version_history(project_id: str, artifact_type: str):
    """Get version history for artifact type."""
    try:
        from src.server.modules.artifact_store import ArtifactStore

        history = ArtifactStore.get_version_history(project_id, artifact_type)
        return {
            "artifact_type": history.artifact_type,
            "project_id": history.project_id,
            "active_version_id": history.active_version_id,
            "versions": [
                {
                    "version_id": v.version_id,
                    "status": v.status,
                    "created_at": v.created_at.isoformat(),
                    "upstream_versions": v.upstream_versions
                }
                for v in history.versions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/versions/{artifact_type}/{version_id}/switch")
async def switch_version(project_id: str, artifact_type: str, version_id: str):
    """Switch to specified version."""
    try:
        from src.server.modules.artifact_store import ArtifactStore

        version = ArtifactStore.switch_to_version(project_id, artifact_type, version_id)
        return {
            "version_id": version.version_id,
            "artifact_type": version.artifact_type,
            "status": version.status,
            "created_at": version.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/versions/{artifact_type}/{v1_id}/diff/{v2_id}")
async def get_version_diff(project_id: str, artifact_type: str, v1_id: str, v2_id: str):
    """Compare two versions."""
    try:
        from src.server.modules.artifact_store import ArtifactStore

        diff = ArtifactStore.get_version_diff(project_id, v1_id, v2_id)
        return diff
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/runs")
async def get_runs(project_id: str):
    """Get all runs for project."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecordEnhanced

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            runs = session.query(RunRecordEnhanced).filter_by(
                project_id=project_id
            ).order_by(RunRecordEnhanced.started_at.desc()).all()

            return {
                "total_runs": len(runs),
                "runs": [
                    {
                        "run_id": r.run_id,
                        "run_type": r.run_type,
                        "state": r.state,
                        "started_at": r.started_at.isoformat(),
                        "ended_at": r.ended_at.isoformat() if r.ended_at else None
                    }
                    for r in runs
                ]
            }
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/runs/{run_id}/resume")
async def resume_run(project_id: str, run_id: str, request: dict = None):
    """Resume execution from failure point."""
    try:
        failed_stage = request.get("failed_stage", "edit_planning") if request else "edit_planning"

        export_bundle = await RunOrchestrator.resume_from_failure(
            project_id, run_id, failed_stage
        )

        return {
            "export_id": export_bundle.export_id,
            "version_id": export_bundle.version_id,
            "video_path": export_bundle.video_path,
            "status": export_bundle.status,
            "created_at": export_bundle.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/runs/{run_id}/diagnostics")
async def get_run_diagnostics(project_id: str, run_id: str, format: str = "json"):
    """Get diagnostic bundle for run."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import RunRecordEnhanced

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            run_record = session.query(RunRecordEnhanced).filter_by(
                run_id=run_id
            ).first()

            if not run_record:
                raise HTTPException(status_code=404, detail="Run not found")

            bundle = DiagnosticReporter.generate_diagnostic_bundle(
                project_id, run_id, run_record,
                performance_metrics=run_record.performance_metrics
            )

            if format == "markdown":
                return {"content": DiagnosticReporter.export_diagnostic_bundle(bundle, "markdown")}
            elif format == "html":
                return {"content": DiagnosticReporter.export_diagnostic_bundle(bundle, "html")}
            else:
                return bundle.dict()

        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/runs/{run_id}/retry/{stage_name}")
async def retry_stage(project_id: str, run_id: str, stage_name: str):
    """Retry specific stage."""
    try:
        from src.server.storage.database import get_or_create_db
        from src.server.storage.schemas import TaskStateRecordEnhanced

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            task = session.query(TaskStateRecordEnhanced).filter(
                TaskStateRecordEnhanced.run_id == run_id,
                TaskStateRecordEnhanced.stage_name == stage_name
            ).first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            # Reset task state for retry
            task.status = "running"
            task.attempt += 1
            task.started_at = datetime.utcnow()
            task.ended_at = None
            task.error_message = None
            session.commit()

            return {
                "task_id": task.task_id,
                "stage_name": task.stage_name,
                "attempt": task.attempt,
                "status": task.status
            }
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
