"""Story Skeleton module - generates and manages story skeleton versions."""

import uuid
from typing import List, Optional
from datetime import datetime

from src.shared.types import StorySegment, StorySkeleton
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import StorySkeletonRecord, StorySegmentRecord


class StorySkeleton:
    """Generate and manage story skeleton versions."""

    @staticmethod
    def generate_skeleton(
        project_id: str, story_segments: List[StorySegment]
    ) -> StorySkeleton:
        """
        Generate story skeleton from parsed segments.

        Steps:
        1. Validate segment count (3-8)
        2. Assign skeleton_id and version
        3. Calculate narrative coverage and confidence
        4. Create StorySkeleton record in DB
        5. Create StorySegment records in DB
        6. Return StorySkeleton
        """
        if not story_segments or len(story_segments) < 3:
            raise ValueError("Skeleton must have at least 3 segments")

        if len(story_segments) > 8:
            raise ValueError("Skeleton cannot have more than 8 segments")

        skeleton_id = str(uuid.uuid4())

        total_chars = sum(seg.end_index - seg.start_index for seg in story_segments)
        narrative_coverage = total_chars / 1000.0 if total_chars > 0 else 0.0
        narrative_coverage = min(1.0, narrative_coverage)

        avg_confidence = (
            sum(seg.confidence for seg in story_segments) / len(story_segments)
            if story_segments
            else 0.0
        )

        skeleton = StorySkeleton(
            skeleton_id=skeleton_id,
            project_id=project_id,
            version=1,
            segments=story_segments,
            total_segments=len(story_segments),
            narrative_coverage=narrative_coverage,
            parsing_confidence=avg_confidence,
            status="draft",
            created_at=datetime.utcnow(),
            confirmed_at=None,
            user_edits=None,
        )

        StorySkeleton._persist_skeleton(project_id, skeleton)

        return skeleton

    @staticmethod
    def get_skeleton(project_id: str, skeleton_id: str) -> Optional[StorySkeleton]:
        """Retrieve skeleton and all segments from DB."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            skeleton_record = session.query(StorySkeletonRecord).filter_by(
                skeleton_id=skeleton_id, project_id=project_id
            ).first()

            if not skeleton_record:
                return None

            segment_records = session.query(StorySegmentRecord).filter_by(
                skeleton_id=skeleton_id
            ).all()

            segments = [
                StorySegment(
                    segment_id=sr.segment_id,
                    title=sr.title,
                    summary=sr.summary,
                    start_index=sr.start_index,
                    end_index=sr.end_index,
                    importance=sr.importance,
                    confidence=sr.confidence,
                    keywords=sr.keywords or [],
                    locations=sr.locations or [],
                    timestamps=sr.timestamps or [],
                )
                for sr in segment_records
            ]

            skeleton = StorySkeleton(
                skeleton_id=skeleton_record.skeleton_id,
                project_id=skeleton_record.project_id,
                version=skeleton_record.version,
                segments=segments,
                total_segments=skeleton_record.total_segments,
                narrative_coverage=skeleton_record.narrative_coverage,
                parsing_confidence=skeleton_record.parsing_confidence,
                status=skeleton_record.status,
                created_at=skeleton_record.created_at,
                confirmed_at=skeleton_record.confirmed_at,
                user_edits=skeleton_record.user_edits,
            )

            return skeleton
        finally:
            session.close()

    @staticmethod
    def get_current_skeleton(project_id: str) -> Optional[StorySkeleton]:
        """Get latest confirmed skeleton, or draft if none confirmed."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            confirmed = session.query(StorySkeletonRecord).filter_by(
                project_id=project_id, status="confirmed"
            ).order_by(StorySkeletonRecord.confirmed_at.desc()).first()

            if confirmed:
                return StorySkeleton.get_skeleton(project_id, confirmed.skeleton_id)

            draft = session.query(StorySkeletonRecord).filter_by(
                project_id=project_id, status="draft"
            ).order_by(StorySkeletonRecord.created_at.desc()).first()

            if draft:
                return StorySkeleton.get_skeleton(project_id, draft.skeleton_id)

            return None
        finally:
            session.close()

    @staticmethod
    def _persist_skeleton(project_id: str, skeleton: StorySkeleton) -> None:
        """Persist skeleton and segments to database."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            skeleton_record = StorySkeletonRecord(
                skeleton_id=skeleton.skeleton_id,
                project_id=project_id,
                version=skeleton.version,
                total_segments=skeleton.total_segments,
                narrative_coverage=skeleton.narrative_coverage,
                parsing_confidence=skeleton.parsing_confidence,
                status=skeleton.status,
                user_edits=skeleton.user_edits,
                created_at=skeleton.created_at,
                confirmed_at=skeleton.confirmed_at,
            )
            session.add(skeleton_record)

            for segment in skeleton.segments:
                segment_record = StorySegmentRecord(
                    segment_id=segment.segment_id,
                    project_id=project_id,
                    skeleton_id=skeleton.skeleton_id,
                    title=segment.title,
                    summary=segment.summary,
                    start_index=segment.start_index,
                    end_index=segment.end_index,
                    importance=segment.importance,
                    confidence=segment.confidence,
                    keywords=segment.keywords,
                    locations=segment.locations,
                    timestamps=segment.timestamps,
                    created_at=datetime.utcnow(),
                )
                session.add(segment_record)

            session.commit()
        finally:
            session.close()
