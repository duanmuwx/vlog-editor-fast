"""Video rendering and export."""

import uuid
import os
import json
from datetime import datetime
from typing import List
from src.shared.types import ExportBundle, Subtitle, Timeline
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    ExportRecord, TimelineRecord, AudioMixRecord, NarrationRecord
)
from src.server.modules.artifact_store import ArtifactStore


class Renderer:
    """Renders final video with subtitles and exports."""

    VIDEO_CODEC = "h264"
    VIDEO_RESOLUTION = "1920x1080"
    VIDEO_ASPECT_RATIO = "16:9"
    VIDEO_BITRATE = "5000k"

    @staticmethod
    def render_export(
        project_id: str,
        timeline_id: str,
        audio_mix_id: str,
        narration_id: str
    ) -> ExportBundle:
        """
        Render final video and export.

        Args:
            project_id: Project ID
            timeline_id: Timeline ID
            audio_mix_id: Audio mix ID
            narration_id: Narration ID

        Returns:
            ExportBundle with MP4, subtitles, narration, manifest
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Get records
            timeline_record = session.query(TimelineRecord).filter_by(
                timeline_id=timeline_id
            ).first()

            audio_mix_record = session.query(AudioMixRecord).filter_by(
                audio_mix_id=audio_mix_id
            ).first()

            narration_record = session.query(NarrationRecord).filter_by(
                narration_id=narration_id
            ).first()

            if not all([timeline_record, audio_mix_record, narration_record]):
                raise ValueError("Missing timeline, audio mix, or narration")

            # Create export directory
            export_dir = os.path.expanduser(f"~/.vlog-editor/projects/{project_id}/exports")
            os.makedirs(export_dir, exist_ok=True)

            # Compose video
            video_path = Renderer._compose_video(project_id, timeline_id, export_dir)

            # Render subtitles onto video
            video_with_subtitles = Renderer._render_subtitles(
                project_id, narration_id, video_path, export_dir
            )

            # Mux audio and video
            final_video_path = Renderer._mux_audio_video(
                video_with_subtitles,
                audio_mix_record.mixed_audio_path,
                export_dir
            )

            # Export SRT subtitles
            subtitle_path = Renderer._export_srt(
                project_id, narration_id, export_dir
            )

            # Export narration MP3
            narration_path = narration_record.tts_audio_path

            # Generate manifest
            manifest_path = Renderer._generate_manifest(
                project_id, timeline_id, final_video_path, export_dir
            )

            # Create ExportBundle
            export_id = str(uuid.uuid4())
            version_id = ArtifactStore.create_version(
                "export",
                project_id,
                upstream_versions={
                    "timeline": timeline_id,
                    "audio_mix": audio_mix_id,
                    "narration": narration_id
                }
            )

            export_bundle = ExportBundle(
                export_id=export_id,
                project_id=project_id,
                version_id=version_id,
                video_path=final_video_path,
                subtitle_path=subtitle_path,
                narration_path=narration_path,
                manifest_path=manifest_path,
                status="success",
                created_at=datetime.utcnow()
            )

            # Persist to database
            Renderer._persist_export(project_id, export_bundle, session)

            return export_bundle

        finally:
            session.close()

    @staticmethod
    def _compose_video(
        project_id: str,
        timeline_id: str,
        export_dir: str
    ) -> str:
        """
        Compose video from clips and transitions.

        For now, returns placeholder path. In production, would use FFmpeg
        to compose video from media clips with transitions.
        """
        video_path = os.path.join(export_dir, "composed_video.mp4")

        # Create placeholder file
        with open(video_path, 'wb') as f:
            f.write(b"placeholder video")

        return video_path

    @staticmethod
    def _render_subtitles(
        project_id: str,
        narration_id: str,
        video_path: str,
        export_dir: str
    ) -> str:
        """
        Render subtitles onto video.

        For now, returns video path unchanged. In production, would use FFmpeg
        to render subtitles onto video using subtitle filter.
        """
        # In production: ffmpeg -i video.mp4 -vf subtitles=subs.srt output.mp4
        return video_path

    @staticmethod
    def _mux_audio_video(
        video_path: str,
        audio_path: str,
        export_dir: str
    ) -> str:
        """
        Mux audio and video.

        For now, returns video path unchanged. In production, would use FFmpeg
        to mux audio and video streams.
        """
        final_path = os.path.join(export_dir, "final_video.mp4")

        # Create placeholder file
        with open(final_path, 'wb') as f:
            f.write(b"placeholder final video")

        return final_path

    @staticmethod
    def _export_srt(
        project_id: str,
        narration_id: str,
        export_dir: str
    ) -> str:
        """Export subtitles as SRT file."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.storage.schemas import SubtitleRecord

            subtitles = session.query(SubtitleRecord).filter_by(
                narration_id=narration_id
            ).order_by(SubtitleRecord.start_time).all()

            srt_path = os.path.join(export_dir, "subtitles.srt")

            with open(srt_path, 'w', encoding='utf-8') as f:
                for i, subtitle in enumerate(subtitles, 1):
                    start_time = Renderer._format_srt_time(subtitle.start_time)
                    end_time = Renderer._format_srt_time(subtitle.end_time)

                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle.text}\n\n")

            return srt_path

        finally:
            session.close()

    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """Format time for SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _generate_manifest(
        project_id: str,
        timeline_id: str,
        video_path: str,
        export_dir: str
    ) -> str:
        """Generate manifest JSON with metadata."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            from src.server.storage.schemas import TimelineRecord

            timeline_record = session.query(TimelineRecord).filter_by(
                timeline_id=timeline_id
            ).first()

            manifest = {
                "project_id": project_id,
                "timeline_id": timeline_id,
                "video_path": video_path,
                "total_duration_seconds": timeline_record.total_duration_seconds if timeline_record else 0,
                "target_duration_seconds": timeline_record.target_duration_seconds if timeline_record else 240,
                "video_codec": Renderer.VIDEO_CODEC,
                "video_resolution": Renderer.VIDEO_RESOLUTION,
                "video_aspect_ratio": Renderer.VIDEO_ASPECT_RATIO,
                "created_at": datetime.utcnow().isoformat()
            }

            manifest_path = os.path.join(export_dir, "manifest.json")

            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)

            return manifest_path

        finally:
            session.close()

    @staticmethod
    def _persist_export(
        project_id: str,
        export_bundle: ExportBundle,
        session
    ) -> None:
        """Persist export to database."""
        export_record = ExportRecord(
            export_id=export_bundle.export_id,
            project_id=project_id,
            version_id=export_bundle.version_id,
            video_path=export_bundle.video_path,
            subtitle_path=export_bundle.subtitle_path,
            narration_path=export_bundle.narration_path,
            manifest_path=export_bundle.manifest_path,
            status=export_bundle.status,
            created_at=export_bundle.created_at
        )
        session.add(export_record)
        session.commit()
