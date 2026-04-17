"""Edit planning - generate timeline from story and highlights."""

import uuid
from datetime import datetime
from typing import List, Optional
from src.shared.types import Timeline, TimelineSegment, TimelineClip, StorySegment, HighlightSelection
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    TimelineRecord, TimelineSegmentRecord, TimelineClipRecord,
    StorySegmentRecord, HighlightSelectionRecord, MediaShotRecord
)
from src.server.modules.artifact_store import ArtifactStore


class EditPlanner:
    """Generates executable timeline from story and highlights."""

    TARGET_DURATION_MIN = 120.0  # 2 minutes
    TARGET_DURATION_MAX = 240.0  # 4 minutes
    DEFAULT_TRANSITION = "cut"
    SEGMENT_BOUNDARY_TRANSITION = "fade"

    @staticmethod
    def plan_edit(project_id: str) -> Timeline:
        """
        Generate timeline from confirmed story and highlights.

        Args:
            project_id: Project ID

        Returns:
            Timeline with clips, transitions, and timing
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            # Get confirmed skeleton segments
            segments = session.query(StorySegmentRecord).filter_by(
                project_id=project_id
            ).order_by(StorySegmentRecord.start_index).all()

            if not segments:
                raise ValueError("No story segments found")

            # Get highlight selections
            selections = session.query(HighlightSelectionRecord).filter_by(
                project_id=project_id
            ).all()

            if not selections:
                raise ValueError("No highlight selections found")

            # Create timeline
            timeline_id = str(uuid.uuid4())
            version_id = ArtifactStore.create_version(
                "timeline",
                project_id,
                upstream_versions={"skeleton": "confirmed", "highlights": "confirmed"}
            )

            timeline_segments = []
            total_duration = 0.0
            current_time = 0.0

            for segment in segments:
                # Find selection for this segment
                selection = next(
                    (s for s in selections if s.segment_id == segment.segment_id),
                    None
                )

                if not selection:
                    continue

                # Get shot details
                shot = session.query(MediaShotRecord).filter_by(
                    shot_id=selection.selected_shot_id
                ).first()

                if not shot:
                    continue

                # Create clip
                shot_duration = shot.duration or 5.0  # Default 5 seconds for photos
                clip = TimelineClip(
                    clip_id=str(uuid.uuid4()),
                    shot_id=shot.shot_id,
                    start_time=current_time,
                    end_time=current_time + shot_duration,
                    transition=EditPlanner.DEFAULT_TRANSITION,
                    duration=shot_duration
                )

                # Create timeline segment
                narration_start = current_time
                narration_end = current_time + shot_duration
                segment_duration = shot_duration

                timeline_segment = TimelineSegment(
                    segment_id=segment.segment_id,
                    clips=[clip],
                    narration_start=narration_start,
                    narration_end=narration_end,
                    total_duration=segment_duration
                )

                timeline_segments.append(timeline_segment)
                current_time += shot_duration
                total_duration += shot_duration

            # Compress if needed
            if total_duration > EditPlanner.TARGET_DURATION_MAX:
                timeline_segments = EditPlanner._compress_to_duration(
                    timeline_segments,
                    EditPlanner.TARGET_DURATION_MAX
                )
                total_duration = sum(seg.total_duration for seg in timeline_segments)

            # Create Timeline
            timeline = Timeline(
                timeline_id=timeline_id,
                project_id=project_id,
                version_id=version_id,
                segments=timeline_segments,
                total_duration_seconds=total_duration,
                target_duration_seconds=EditPlanner.TARGET_DURATION_MAX,
                created_at=datetime.utcnow()
            )

            # Persist to database
            EditPlanner._persist_timeline(project_id, timeline, session)

            return timeline

        finally:
            session.close()

    @staticmethod
    def _compress_to_duration(
        segments: List[TimelineSegment],
        target_seconds: float
    ) -> List[TimelineSegment]:
        """
        Compress timeline to target duration by removing low-importance clips.

        Args:
            segments: Timeline segments
            target_seconds: Target duration in seconds

        Returns:
            Compressed segments
        """
        current_duration = sum(seg.total_duration for seg in segments)

        if current_duration <= target_seconds:
            return segments

        # Calculate how much to remove
        to_remove = current_duration - target_seconds
        removed = 0.0

        # Remove from end (lower importance segments typically at end)
        compressed = []
        for segment in reversed(segments):
            if removed >= to_remove:
                compressed.insert(0, segment)
            else:
                removed += segment.total_duration

        return compressed if compressed else segments

    @staticmethod
    def _persist_timeline(
        project_id: str,
        timeline: Timeline,
        session
    ) -> None:
        """Persist timeline to database."""
        # Create timeline record
        timeline_record = TimelineRecord(
            timeline_id=timeline.timeline_id,
            project_id=project_id,
            version_id=timeline.version_id,
            total_duration_seconds=timeline.total_duration_seconds,
            target_duration_seconds=timeline.target_duration_seconds,
            created_at=timeline.created_at
        )
        session.add(timeline_record)
        session.flush()

        # Create timeline segment records
        for segment in timeline.segments:
            segment_record = TimelineSegmentRecord(
                segment_id=str(uuid.uuid4()),
                timeline_id=timeline.timeline_id,
                story_segment_id=segment.segment_id,
                narration_start=segment.narration_start,
                narration_end=segment.narration_end,
                total_duration=segment.total_duration
            )
            session.add(segment_record)
            session.flush()

            # Create clip records
            for clip in segment.clips:
                clip_record = TimelineClipRecord(
                    clip_id=clip.clip_id,
                    segment_id=segment_record.segment_id,
                    shot_id=clip.shot_id,
                    start_time=clip.start_time,
                    end_time=clip.end_time,
                    transition=clip.transition
                )
                session.add(clip_record)

        session.commit()
