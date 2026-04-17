"""Project API routes."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from src.shared.types import ProjectInputContract
from src.server.modules.project_manager import ProjectManager
from src.server.modules.input_validator import InputValidator
from src.server.modules.asset_indexer import AssetIndexer

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
