"""Audio composition - mix narration, ambient sound, and BGM."""

import uuid
import os
from datetime import datetime
from typing import List
from src.shared.types import AudioMixPack, AudioTrack
from src.server.storage.database import get_or_create_db, get_project_subdir
from src.server.storage.schemas import (
    AudioMixRecord,
    AudioTrackRecord,
    NarrationRecord,
    TimelineRecord,
)
from src.server.modules.artifact_store import ArtifactStore


class AudioComposer:
    """Mixes narration, ambient sound, and BGM."""

    NARRATION_VOLUME = 0.8  # -20dB equivalent
    AMBIENT_VOLUME = 0.3  # -30dB equivalent
    BGM_VOLUME = 0.5  # -25dB equivalent
    MIN_AMBIENT_MOMENTS = 3

    @staticmethod
    def compose_audio(
        project_id: str, timeline_id: str, narration_id: str, bgm_asset: str
    ) -> AudioMixPack:
        """
        Mix narration, ambient sound, and BGM.

        Args:
            project_id: Project ID
            timeline_id: Timeline ID
            narration_id: Narration ID
            bgm_asset: Path to BGM asset

        Returns:
            AudioMixPack with mixed audio
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Get timeline and narration
            timeline_record = (
                session.query(TimelineRecord).filter_by(timeline_id=timeline_id).first()
            )

            narration_record = (
                session.query(NarrationRecord).filter_by(narration_id=narration_id).first()
            )

            if not timeline_record or not narration_record:
                raise ValueError("Timeline or narration not found")

            total_duration = timeline_record.total_duration_seconds

            # Create audio tracks
            tracks = []

            # Add narration track
            narration_track = AudioTrack(
                track_id=str(uuid.uuid4()),
                track_type="narration",
                file_path=narration_record.tts_audio_path,
                volume=AudioComposer.NARRATION_VOLUME,
                start_time=0.0,
                end_time=total_duration,
            )
            tracks.append(narration_track)

            # Add ambient sound tracks (placeholder)
            ambient_tracks = AudioComposer._extract_ambient_sound(
                project_id, timeline_id, total_duration, session
            )
            tracks.extend(ambient_tracks)

            # Add BGM track
            if bgm_asset and os.path.exists(bgm_asset):
                bgm_track = AudioTrack(
                    track_id=str(uuid.uuid4()),
                    track_type="bgm",
                    file_path=bgm_asset,
                    volume=AudioComposer.BGM_VOLUME,
                    start_time=0.0,
                    end_time=total_duration,
                )
                tracks.append(bgm_track)

            # Mix audio
            mixed_audio_path = AudioComposer._mix_tracks(project_id, tracks, total_duration)

            # Create AudioMixPack
            audio_mix_id = str(uuid.uuid4())
            version_id = ArtifactStore.create_version(
                "audio_mix",
                project_id,
                upstream_versions={"timeline": timeline_id, "narration": narration_id},
            )

            audio_mix_pack = AudioMixPack(
                audio_mix_id=audio_mix_id,
                project_id=project_id,
                version_id=version_id,
                tracks=tracks,
                mixed_audio_path=mixed_audio_path,
                total_duration_seconds=total_duration,
                created_at=datetime.utcnow(),
            )

            # Persist to database
            AudioComposer._persist_audio_mix(project_id, audio_mix_pack, session)

            return audio_mix_pack

        finally:
            session.close()

    @staticmethod
    def _extract_ambient_sound(
        project_id: str, timeline_id: str, total_duration: float, session
    ) -> List[AudioTrack]:
        """
        Extract ambient sound from video clips.

        For now, returns placeholder tracks. In production, would extract
        audio from video files and identify ambient sound moments.
        """
        ambient_tracks = []

        # Create placeholder ambient tracks at different times
        moment_duration = 5.0
        num_moments = min(AudioComposer.MIN_AMBIENT_MOMENTS, int(total_duration / 30))

        for i in range(num_moments):
            start_time = (i + 1) * (total_duration / (num_moments + 1))
            end_time = min(start_time + moment_duration, total_duration)

            ambient_track = AudioTrack(
                track_id=str(uuid.uuid4()),
                track_type="ambient",
                file_path=f"ambient_{i}.wav",  # Placeholder
                volume=AudioComposer.AMBIENT_VOLUME,
                start_time=start_time,
                end_time=end_time,
            )
            ambient_tracks.append(ambient_track)

        return ambient_tracks

    @staticmethod
    def _mix_tracks(project_id: str, tracks: List[AudioTrack], total_duration: float) -> str:
        """
        Mix audio tracks using FFmpeg.

        For now, returns placeholder path. In production, would use FFmpeg
        to mix multiple audio tracks with volume control.
        """
        audio_dir = str(get_project_subdir(project_id, "audio"))

        mixed_audio_path = os.path.join(audio_dir, "mixed_audio.wav")

        # Create placeholder file
        with open(mixed_audio_path, "wb") as f:
            f.write(b"placeholder mixed audio")

        return mixed_audio_path

    @staticmethod
    def _persist_audio_mix(project_id: str, audio_mix_pack: AudioMixPack, session) -> None:
        """Persist audio mix to database."""
        # Create audio mix record
        mix_record = AudioMixRecord(
            audio_mix_id=audio_mix_pack.audio_mix_id,
            project_id=project_id,
            version_id=audio_mix_pack.version_id,
            mixed_audio_path=audio_mix_pack.mixed_audio_path,
            total_duration_seconds=audio_mix_pack.total_duration_seconds,
            created_at=audio_mix_pack.created_at,
        )
        session.add(mix_record)
        session.flush()

        # Create audio track records
        for track in audio_mix_pack.tracks:
            track_record = AudioTrackRecord(
                track_id=track.track_id,
                audio_mix_id=audio_mix_pack.audio_mix_id,
                track_type=track.track_type,
                file_path=track.file_path,
                volume=track.volume,
                start_time=track.start_time,
                end_time=track.end_time,
            )
            session.add(track_record)

        session.commit()
