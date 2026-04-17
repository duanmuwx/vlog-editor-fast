"""Narration generation - TTS, subtitles, and text cards."""

import uuid
import os
from datetime import datetime
from typing import List, Tuple
from src.shared.types import NarrationPack, Subtitle, TextCard, Timeline
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    NarrationRecord, SubtitleRecord, TextCardRecord,
    StorySegmentRecord, TimelineRecord
)
from src.server.modules.artifact_store import ArtifactStore


class NarrationEngine:
    """Generates voiceover, subtitles, and text cards."""

    MAX_NARRATION_PER_SEGMENT = 20.0  # seconds
    SUBTITLE_CHUNK_DURATION = 5.0  # seconds per subtitle

    @staticmethod
    def generate_narration(
        project_id: str,
        timeline_id: str,
        tts_voice: str
    ) -> NarrationPack:
        """
        Generate narration, subtitles, and text cards.

        Args:
            project_id: Project ID
            timeline_id: Timeline ID
            tts_voice: TTS voice to use

        Returns:
            NarrationPack with audio and subtitles
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Get timeline
            timeline_record = session.query(TimelineRecord).filter_by(
                timeline_id=timeline_id
            ).first()

            if not timeline_record:
                raise ValueError(f"Timeline {timeline_id} not found")

            # Generate narration text
            narration_text = NarrationEngine._generate_narration_text(
                project_id, session
            )

            # Call TTS API
            tts_audio_path, audio_duration = NarrationEngine._call_tts_api(
                narration_text,
                tts_voice,
                project_id
            )

            # Generate subtitles
            subtitles = NarrationEngine._generate_subtitles(
                narration_text,
                audio_duration
            )

            # Generate text cards
            text_cards = NarrationEngine._generate_text_cards(
                project_id, session
            )

            # Create NarrationPack
            narration_id = str(uuid.uuid4())
            version_id = ArtifactStore.create_version(
                "narration",
                project_id,
                upstream_versions={"timeline": timeline_id}
            )

            narration_pack = NarrationPack(
                narration_id=narration_id,
                project_id=project_id,
                version_id=version_id,
                narration_text=narration_text,
                tts_audio_path=tts_audio_path,
                subtitles=subtitles,
                text_cards=text_cards,
                tts_voice=tts_voice,
                created_at=datetime.utcnow()
            )

            # Persist to database
            NarrationEngine._persist_narration(project_id, narration_pack, session)

            return narration_pack

        finally:
            session.close()

    @staticmethod
    def _generate_narration_text(project_id: str, session) -> str:
        """Generate narration text from story segments."""
        segments = session.query(StorySegmentRecord).filter_by(
            project_id=project_id
        ).order_by(StorySegmentRecord.start_index).all()

        narration_parts = []
        for segment in segments:
            narration_parts.append(segment.summary)

        return " ".join(narration_parts)

    @staticmethod
    def _call_tts_api(
        text: str,
        voice: str,
        project_id: str
    ) -> Tuple[str, float]:
        """
        Call TTS API to generate audio.

        Args:
            text: Text to convert to speech
            voice: Voice to use
            project_id: Project ID for file storage

        Returns:
            Tuple of (audio_path, duration_seconds)
        """
        # For now, create a placeholder audio file
        # In production, this would call Azure TTS, Google TTS, etc.
        audio_dir = os.path.expanduser(f"~/.vlog-editor/projects/{project_id}/audio")
        os.makedirs(audio_dir, exist_ok=True)

        audio_path = os.path.join(audio_dir, f"narration_{voice}.mp3")

        # Estimate duration: ~150 words per minute = 2.5 words per second
        word_count = len(text.split())
        estimated_duration = word_count / 2.5

        # Create placeholder file
        with open(audio_path, 'wb') as f:
            f.write(b"placeholder audio")

        return audio_path, estimated_duration

    @staticmethod
    def _generate_subtitles(
        text: str,
        audio_duration: float
    ) -> List[Subtitle]:
        """Generate subtitles from narration text."""
        words = text.split()
        words_per_chunk = max(1, int(len(words) * NarrationEngine.SUBTITLE_CHUNK_DURATION / audio_duration))

        subtitles = []
        current_time = 0.0

        for i in range(0, len(words), words_per_chunk):
            chunk_words = words[i:i + words_per_chunk]
            chunk_text = " ".join(chunk_words)

            subtitle = Subtitle(
                subtitle_id=str(uuid.uuid4()),
                text=chunk_text,
                start_time=current_time,
                end_time=current_time + NarrationEngine.SUBTITLE_CHUNK_DURATION
            )
            subtitles.append(subtitle)
            current_time += NarrationEngine.SUBTITLE_CHUNK_DURATION

        return subtitles

    @staticmethod
    def _generate_text_cards(project_id: str, session) -> List[TextCard]:
        """Generate text cards for segment transitions."""
        segments = session.query(StorySegmentRecord).filter_by(
            project_id=project_id
        ).order_by(StorySegmentRecord.start_index).all()

        text_cards = []
        for i, segment in enumerate(segments, 1):
            text_card = TextCard(
                card_id=str(uuid.uuid4()),
                text=segment.title,
                duration_seconds=3.0,
                position="center"
            )
            text_cards.append(text_card)

        return text_cards

    @staticmethod
    def _persist_narration(
        project_id: str,
        narration_pack: NarrationPack,
        session
    ) -> None:
        """Persist narration to database."""
        # Create narration record
        narration_record = NarrationRecord(
            narration_id=narration_pack.narration_id,
            project_id=project_id,
            version_id=narration_pack.version_id,
            narration_text=narration_pack.narration_text,
            tts_audio_path=narration_pack.tts_audio_path,
            tts_voice=narration_pack.tts_voice,
            created_at=narration_pack.created_at
        )
        session.add(narration_record)
        session.flush()

        # Create subtitle records
        for subtitle in narration_pack.subtitles:
            subtitle_record = SubtitleRecord(
                subtitle_id=subtitle.subtitle_id,
                narration_id=narration_pack.narration_id,
                text=subtitle.text,
                start_time=subtitle.start_time,
                end_time=subtitle.end_time
            )
            session.add(subtitle_record)

        # Create text card records
        for text_card in narration_pack.text_cards:
            card_record = TextCardRecord(
                card_id=text_card.card_id,
                narration_id=narration_pack.narration_id,
                text=text_card.text,
                duration_seconds=text_card.duration_seconds,
                position=text_card.position
            )
            session.add(card_record)

        session.commit()
