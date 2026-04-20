"""Integration tests for Phase 7 desktop-facing API supplements."""

import asyncio
from pathlib import Path

from src.server.api.projects import create_project, delete_project, get_assets, list_projects, validate_project
from src.shared.types import ProjectInputContract


def _create_media_files(media_dir: Path) -> list[str]:
    media_dir.mkdir(parents=True, exist_ok=True)
    video_path = media_dir / "clip_01.mp4"
    photo_path = media_dir / "photo_01.jpg"
    video_path.write_bytes(b"dummy video content")
    photo_path.write_bytes(b"dummy photo content")
    return [str(video_path), str(photo_path)]


def test_phase7_api_list_assets_validate_and_delete(tmp_path, monkeypatch):
    """Desktop contract endpoints return list, asset details, revalidation, and deletion."""
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / ".vlog-editor"))
    media_files = _create_media_files(tmp_path / "media")

    create_payload = ProjectInputContract(
        project_name="Phase 7 Contract Test",
        travel_note="这是一段足够长的旅行叙事。" * 20,
        media_files=media_files,
        bgm_asset=None,
        tts_voice="default",
        metadata_pack={"season": "spring"},
    )

    create_response = asyncio.run(create_project(create_payload))
    project_id = create_response["project_id"]

    list_payload = asyncio.run(list_projects())
    assert list_payload["total_projects"] == 1
    assert list_payload["projects"][0]["project_id"] == project_id
    assert list_payload["projects"][0]["total_videos"] == 1
    assert list_payload["projects"][0]["total_photos"] == 1

    assets_payload = asyncio.run(get_assets(project_id))
    assert len(assets_payload["media_items"]) == 2
    assert {item["file_type"] for item in assets_payload["media_items"]} == {"video", "photo"}
    assert all("file_id" in item for item in assets_payload["media_items"])

    validation_payload = asyncio.run(validate_project(project_id))["validation_report"]
    assert validation_payload["project_id"] == project_id
    assert validation_payload["media_summary"]["total_files"] == 2
    assert "No media files provided" not in validation_payload["errors"]

    delete_response = asyncio.run(delete_project(project_id))
    assert delete_response.status_code == 204

    list_after_delete = asyncio.run(list_projects())
    assert list_after_delete["total_projects"] == 0
