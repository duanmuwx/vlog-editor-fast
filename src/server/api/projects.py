"""Project API routes."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from src.shared.types import ProjectInputContract, SkeletonConfirmationRequest
from src.server.modules.project_manager import ProjectManager
from src.server.modules.input_validator import InputValidator
from src.server.modules.asset_indexer import AssetIndexer
from src.server.modules.story_parser import StoryParser
from src.server.modules.story_skeleton import StorySkeleton
from src.server.modules.skeleton_confirmation import SkeletonConfirmation

router = APIRouter(prefix="/api/projects", tags=["projects"])


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


@router.post("/{project_id}/validate")
async def validate_project(project_id: str):
    """Validate project input."""
    try:
        config = ProjectManager.get_project_config(project_id)
        if not config:
            raise HTTPException(status_code=404, detail="Project not found")

        # Reconstruct input contract
        input_contract = ProjectInputContract(
            project_name="",  # Not stored, would need to retrieve from metadata
            travel_note=config.travel_note,
            media_files=[],  # Would need to retrieve from database
            bgm_asset=config.bgm_asset,
            tts_voice=config.tts_voice,
            metadata_pack=config.metadata_pack
        )

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
        from src.server.storage.schemas import AssetIndexRecord

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            index_record = session.query(AssetIndexRecord).filter(
                AssetIndexRecord.project_id == project_id
            ).first()

            if not index_record:
                raise HTTPException(status_code=404, detail="Asset index not found")

            return {
                "index_id": index_record.index_id,
                "project_id": index_record.project_id,
                "total_videos": index_record.total_videos,
                "total_photos": index_record.total_photos,
                "total_duration": index_record.total_duration,
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
        skeleton = StorySkeleton.get_skeleton(project_id, skeleton_id)
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
        skeleton = StorySkeleton.get_current_skeleton(project_id)
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
