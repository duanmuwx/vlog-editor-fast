"""Highlight Confirmation module - handles user confirmation and selection of highlights."""

import uuid
from typing import List, Dict, Tuple, Optional
from datetime import datetime

from src.shared.types import HighlightSelection
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    HighlightSelectionRecord,
    StorySegmentRecord,
    AlignmentCandidateRecord,
    MediaShotRecord,
)


class HighlightConfirmation:
    """Handle user confirmation and selection of highlights."""

    @staticmethod
    def confirm_highlights(project_id: str, skeleton_id: str, selections: List[Dict]) -> List[HighlightSelection]:
        """
        Confirm user's highlight selections.

        Steps:
        1. Validate selections (all segments have selection, valid shot_ids)
        2. For each selection: create HighlightSelection record
        3. Persist to database
        4. Return confirmed selections
        """
        is_valid, error_msg = HighlightConfirmation._validate_selections(project_id, skeleton_id, selections)
        if not is_valid:
            raise ValueError(f"Invalid selections: {error_msg}")

        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            confirmed_selections = []

            for selection_data in selections:
                segment_id = selection_data.get("segment_id")
                shot_id = selection_data.get("shot_id")
                user_confirmed = selection_data.get("user_confirmed", True)

                candidates = session.query(AlignmentCandidateRecord).filter_by(
                    segment_id=segment_id, project_id=project_id
                ).all()

                alternatives_available = len(candidates) - 1

                selection = HighlightSelection(
                    selection_id=str(uuid.uuid4()),
                    project_id=project_id,
                    segment_id=segment_id,
                    selected_shot_id=shot_id,
                    user_confirmed=user_confirmed,
                    alternatives_available=alternatives_available,
                    confirmed_at=datetime.utcnow() if user_confirmed else None,
                )

                confirmed_selections.append(selection)

            HighlightConfirmation._persist_selections(project_id, confirmed_selections)

            return confirmed_selections
        finally:
            session.close()

    @staticmethod
    def _validate_selections(project_id: str, skeleton_id: str, selections: List[Dict]) -> Tuple[bool, str]:
        """Validate that all segments have valid selections."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            segments = session.query(StorySegmentRecord).filter_by(skeleton_id=skeleton_id).all()
            segment_ids = {seg.segment_id for seg in segments}

            selection_segment_ids = {sel.get("segment_id") for sel in selections}

            if selection_segment_ids != segment_ids:
                missing = segment_ids - selection_segment_ids
                return False, f"Missing selections for segments: {missing}"

            for selection in selections:
                segment_id = selection.get("segment_id")
                shot_id = selection.get("shot_id")

                if not segment_id or not shot_id:
                    return False, "Selection must have segment_id and shot_id"

                candidates = session.query(AlignmentCandidateRecord).filter_by(
                    segment_id=segment_id, shot_id=shot_id, project_id=project_id
                ).first()

                if not candidates:
                    return False, f"Shot {shot_id} is not a valid candidate for segment {segment_id}"

            return True, ""
        finally:
            session.close()

    @staticmethod
    def _persist_selections(project_id: str, selections: List[HighlightSelection]) -> None:
        """Persist highlight selections to database."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            for selection in selections:
                selection_record = HighlightSelectionRecord(
                    selection_id=selection.selection_id,
                    project_id=project_id,
                    segment_id=selection.segment_id,
                    selected_shot_id=selection.selected_shot_id,
                    user_confirmed=selection.user_confirmed,
                    alternatives_available=selection.alternatives_available,
                    confirmed_at=selection.confirmed_at,
                    created_at=datetime.utcnow(),
                )
                session.add(selection_record)

            session.commit()
        finally:
            session.close()

    @staticmethod
    def get_current_highlights(project_id: str) -> Optional[List[HighlightSelection]]:
        """Retrieve current confirmed highlight selections."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            selection_records = session.query(HighlightSelectionRecord).filter_by(
                project_id=project_id, user_confirmed=True
            ).all()

            if not selection_records:
                return None

            selections = [
                HighlightSelection(
                    selection_id=rec.selection_id,
                    project_id=rec.project_id,
                    segment_id=rec.segment_id,
                    selected_shot_id=rec.selected_shot_id,
                    user_confirmed=rec.user_confirmed,
                    alternatives_available=rec.alternatives_available,
                    confirmed_at=rec.confirmed_at,
                )
                for rec in selection_records
            ]

            return selections
        finally:
            session.close()
