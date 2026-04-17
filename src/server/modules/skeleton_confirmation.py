"""Skeleton Confirmation module - handles user confirmation and edits."""

import uuid
from typing import List, Dict, Tuple, Optional
from datetime import datetime

from src.shared.types import StorySegment, StorySkeleton
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    StorySkeletonRecord,
    StorySegmentRecord,
    SkeletonConfirmationRecord,
)
from src.server.modules.story_skeleton import StorySkeleton as SkeletonManager


class SkeletonConfirmation:
    """Handle user confirmation and edits to story skeleton."""

    @staticmethod
    def confirm_skeleton(
        project_id: str, skeleton_id: str, edits: List[Dict]
    ) -> StorySkeleton:
        """
        Apply user edits and confirm skeleton.

        Supported edits:
        - merge: Combine multiple segments into one
        - delete: Remove a segment
        - reorder: Change segment order
        - mark: Mark segment as "must_keep" or "optional"

        Steps:
        1. Retrieve skeleton from DB
        2. Validate edits
        3. Apply edits to segments
        4. Recalculate coverage and confidence
        5. Update skeleton status to "confirmed"
        6. Create skeleton_confirmations record
        7. Return confirmed skeleton
        """
        skeleton = SkeletonManager.get_skeleton(project_id, skeleton_id)
        if not skeleton:
            raise ValueError(f"Skeleton {skeleton_id} not found")

        is_valid, error_msg = SkeletonConfirmation._validate_edits(skeleton, edits)
        if not is_valid:
            raise ValueError(f"Invalid edits: {error_msg}")

        updated_segments = SkeletonConfirmation._apply_edits(skeleton.segments, edits)

        if len(updated_segments) < 3:
            raise ValueError("Skeleton must have at least 3 segments after edits")

        total_chars = sum(seg.end_index - seg.start_index for seg in updated_segments)
        narrative_coverage = min(1.0, total_chars / 1000.0) if total_chars > 0 else 0.0

        avg_confidence = (
            sum(seg.confidence for seg in updated_segments) / len(updated_segments)
            if updated_segments
            else 0.0
        )

        confirmed_skeleton = StorySkeleton(
            skeleton_id=skeleton_id,
            project_id=project_id,
            version=skeleton.version,
            segments=updated_segments,
            total_segments=len(updated_segments),
            narrative_coverage=narrative_coverage,
            parsing_confidence=avg_confidence,
            status="confirmed",
            created_at=skeleton.created_at,
            confirmed_at=datetime.utcnow(),
            user_edits={"edits": edits, "applied_at": datetime.utcnow().isoformat()},
        )

        SkeletonConfirmation._persist_confirmation(project_id, confirmed_skeleton, edits)

        return confirmed_skeleton

    @staticmethod
    def _validate_edits(skeleton: StorySkeleton, edits: List[Dict]) -> Tuple[bool, str]:
        """Validate edit operations."""
        segment_ids = {seg.segment_id for seg in skeleton.segments}

        for edit in edits:
            operation = edit.get("operation")
            segment_ids_in_edit = set(edit.get("segment_ids", []))

            if operation not in ["merge", "delete", "reorder", "mark"]:
                return False, f"Unknown operation: {operation}"

            if operation in ["merge", "delete", "mark"]:
                if not segment_ids_in_edit:
                    return False, f"{operation} requires segment_ids"

                if not segment_ids_in_edit.issubset(segment_ids):
                    return False, f"Invalid segment_ids in {operation}"

            if operation == "reorder":
                if not segment_ids_in_edit:
                    return False, "reorder requires segment_ids"

                if segment_ids_in_edit != segment_ids:
                    return False, "reorder must include all segments"

        return True, ""

    @staticmethod
    def _apply_edits(segments: List[StorySegment], edits: List[Dict]) -> List[StorySegment]:
        """Apply all edit operations to segments."""
        current_segments = list(segments)

        for edit in edits:
            operation = edit.get("operation")
            segment_ids = edit.get("segment_ids", [])

            if operation == "merge":
                current_segments = SkeletonConfirmation._apply_merge(
                    current_segments, segment_ids
                )
            elif operation == "delete":
                current_segments = SkeletonConfirmation._apply_delete(
                    current_segments, segment_ids
                )
            elif operation == "reorder":
                current_segments = SkeletonConfirmation._apply_reorder(
                    current_segments, segment_ids
                )
            elif operation == "mark":
                current_segments = SkeletonConfirmation._apply_mark(
                    current_segments, segment_ids, edit.get("payload", {})
                )

        return current_segments

    @staticmethod
    def _apply_merge(segments: List[StorySegment], segment_ids: List[str]) -> List[StorySegment]:
        """Merge multiple segments into one."""
        to_merge = [seg for seg in segments if seg.segment_id in segment_ids]
        to_keep = [seg for seg in segments if seg.segment_id not in segment_ids]

        if not to_merge:
            return segments

        to_merge.sort(key=lambda s: s.start_index)

        merged_title = " + ".join(seg.title for seg in to_merge)
        merged_summary = " ".join(seg.summary for seg in to_merge)
        merged_keywords = []
        merged_locations = []
        merged_timestamps = []

        for seg in to_merge:
            merged_keywords.extend(seg.keywords)
            merged_locations.extend(seg.locations)
            merged_timestamps.extend(seg.timestamps)

        merged_segment = StorySegment(
            segment_id=str(uuid.uuid4()),
            title=merged_title[:100],
            summary=merged_summary[:200],
            start_index=to_merge[0].start_index,
            end_index=to_merge[-1].end_index,
            importance=to_merge[0].importance,
            confidence=sum(seg.confidence for seg in to_merge) / len(to_merge),
            keywords=list(set(merged_keywords)),
            locations=list(set(merged_locations)),
            timestamps=list(set(merged_timestamps)),
        )

        result = to_keep + [merged_segment]
        result.sort(key=lambda s: s.start_index)

        return result

    @staticmethod
    def _apply_delete(segments: List[StorySegment], segment_ids: List[str]) -> List[StorySegment]:
        """Remove segments."""
        return [seg for seg in segments if seg.segment_id not in segment_ids]

    @staticmethod
    def _apply_reorder(
        segments: List[StorySegment], new_order: List[str]
    ) -> List[StorySegment]:
        """Reorder segments."""
        segment_map = {seg.segment_id: seg for seg in segments}
        return [segment_map[seg_id] for seg_id in new_order if seg_id in segment_map]

    @staticmethod
    def _apply_mark(
        segments: List[StorySegment], segment_ids: List[str], payload: Dict
    ) -> List[StorySegment]:
        """Mark segments with metadata."""
        mark_type = payload.get("mark_type", "optional")

        for seg in segments:
            if seg.segment_id in segment_ids:
                if not hasattr(seg, "metadata"):
                    seg.metadata = {}
                seg.metadata["mark"] = mark_type

        return segments

    @staticmethod
    def _persist_confirmation(
        project_id: str, skeleton: StorySkeleton, edits: List[Dict]
    ) -> None:
        """Persist confirmed skeleton and confirmation record to database."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            skeleton_record = session.query(StorySkeletonRecord).filter_by(
                skeleton_id=skeleton.skeleton_id
            ).first()

            if skeleton_record:
                skeleton_record.status = "confirmed"
                skeleton_record.confirmed_at = skeleton.confirmed_at
                skeleton_record.user_edits = skeleton.user_edits
                skeleton_record.total_segments = skeleton.total_segments
                skeleton_record.narrative_coverage = skeleton.narrative_coverage
                skeleton_record.parsing_confidence = skeleton.parsing_confidence
            else:
                skeleton_record = StorySkeletonRecord(
                    skeleton_id=skeleton.skeleton_id,
                    project_id=project_id,
                    version=skeleton.version,
                    total_segments=skeleton.total_segments,
                    narrative_coverage=skeleton.narrative_coverage,
                    parsing_confidence=skeleton.parsing_confidence,
                    status="confirmed",
                    user_edits=skeleton.user_edits,
                    created_at=skeleton.created_at,
                    confirmed_at=skeleton.confirmed_at,
                )
                session.add(skeleton_record)

            session.query(StorySegmentRecord).filter_by(
                skeleton_id=skeleton.skeleton_id
            ).delete()

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

            confirmation_record = SkeletonConfirmationRecord(
                confirmation_id=str(uuid.uuid4()),
                project_id=project_id,
                skeleton_id=skeleton.skeleton_id,
                edits=edits,
                confirmed_at=datetime.utcnow(),
            )
            session.add(confirmation_record)

            session.commit()
        finally:
            session.close()
