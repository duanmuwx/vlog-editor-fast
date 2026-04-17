"""Alignment Engine module - matches story segments to media using multi-modal signals."""

import uuid
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import re

from src.shared.types import AlignmentCandidate, StorySegment, MediaShot
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import (
    AlignmentCandidateRecord,
    StorySegmentRecord,
    MediaShotRecord,
)


class AlignmentEngine:
    """Match story segments to media shots using multi-modal signals."""

    TEXT_WEIGHT = 0.6
    TIME_WEIGHT = 0.2
    LOCATION_WEIGHT = 0.2
    TOP_N_CANDIDATES = 5

    @staticmethod
    def align_media(project_id: str, skeleton_id: str) -> List[AlignmentCandidate]:
        """
        Align story segments to media shots.

        Steps:
        1. Retrieve story skeleton and segments
        2. Retrieve media shots
        3. For each segment: generate candidate shots
        4. Score each candidate using multi-modal signals
        5. Rank candidates by score
        6. Persist to database
        7. Return all candidates
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            segments = session.query(StorySegmentRecord).filter_by(skeleton_id=skeleton_id).all()
            shots = session.query(MediaShotRecord).filter_by(project_id=project_id).all()

            if not shots:
                return []

            all_candidates = []

            for segment in segments:
                segment_obj = StorySegment(
                    segment_id=segment.segment_id,
                    title=segment.title,
                    summary=segment.summary,
                    start_index=segment.start_index,
                    end_index=segment.end_index,
                    importance=segment.importance,
                    confidence=segment.confidence,
                    keywords=segment.keywords or [],
                    locations=segment.locations or [],
                    timestamps=segment.timestamps or [],
                )

                shots_objs = [
                    MediaShot(
                        shot_id=s.shot_id,
                        file_id=s.file_id,
                        shot_type=s.shot_type,
                        start_time=s.start_time,
                        end_time=s.end_time,
                        duration=s.duration,
                        quality_score=s.quality_score,
                        has_audio=s.has_audio,
                        visual_features=s.visual_features or {},
                        confidence=s.confidence,
                    )
                    for s in shots
                ]

                candidates = AlignmentEngine._generate_candidates(project_id, segment_obj, shots_objs)
                all_candidates.extend(candidates)

            AlignmentEngine._persist_candidates(project_id, all_candidates)

            return all_candidates
        finally:
            session.close()

    @staticmethod
    def _generate_candidates(project_id: str, segment: StorySegment, shots: List[MediaShot]) -> List[AlignmentCandidate]:
        """
        Generate candidate shots for a segment.

        Steps:
        1. Score text-visual match (segment summary vs. visual features)
        2. Score time match (segment timestamps vs. shot timestamps)
        3. Score location match (segment locations vs. photo EXIF)
        4. Combine scores with weights
        5. Filter low-confidence candidates
        6. Return top N candidates
        """
        candidates = []

        for shot in shots:
            text_score = AlignmentEngine._score_text_match(segment.summary, segment.keywords, shot.visual_features)
            time_score = AlignmentEngine._score_time_match(segment.timestamps, shot.start_time)
            location_score = AlignmentEngine._score_location_match(segment.locations, shot.shot_type)

            combined_score = (
                text_score * AlignmentEngine.TEXT_WEIGHT
                + (time_score if time_score is not None else 0.0) * AlignmentEngine.TIME_WEIGHT
                + (location_score if location_score is not None else 0.0) * AlignmentEngine.LOCATION_WEIGHT
            )

            reasoning = AlignmentEngine._generate_reasoning(
                segment, shot, text_score, time_score, location_score
            )

            candidate = AlignmentCandidate(
                candidate_id=str(uuid.uuid4()),
                segment_id=segment.segment_id,
                shot_id=shot.shot_id,
                match_score=combined_score,
                text_match_score=text_score,
                time_match_score=time_score,
                location_match_score=location_score,
                reasoning=reasoning,
            )
            candidates.append(candidate)

        candidates.sort(key=lambda c: c.match_score, reverse=True)
        return candidates[: AlignmentEngine.TOP_N_CANDIDATES]

    @staticmethod
    def _score_text_match(segment_summary: str, keywords: List[str], visual_features: Dict) -> float:
        """
        Score semantic match between text and visual features.

        Simple keyword matching:
        - Check if segment keywords appear in visual features
        - Check if segment summary contains visual feature keywords
        """
        if not visual_features:
            return 0.3

        score = 0.0
        match_count = 0

        summary_lower = segment_summary.lower()
        keywords_lower = [k.lower() for k in keywords]

        for feature_key, feature_value in visual_features.items():
            if isinstance(feature_value, str):
                feature_lower = feature_value.lower()
                if feature_lower in summary_lower or feature_lower in keywords_lower:
                    match_count += 1

        if keywords:
            for keyword in keywords_lower:
                if keyword in summary_lower:
                    match_count += 1

        score = min(1.0, match_count * 0.2)
        return max(0.3, score)

    @staticmethod
    def _score_time_match(segment_timestamps: List[str], shot_start_time: Optional[float]) -> Optional[float]:
        """
        Score match based on time references.

        If segment has timestamps and shot has time info, try to match.
        Otherwise return None (no time data available).
        """
        if not segment_timestamps or shot_start_time is None:
            return None

        try:
            time_patterns = []
            for ts in segment_timestamps:
                numbers = re.findall(r'\d+', ts)
                if numbers:
                    time_patterns.append(int(numbers[0]))

            if not time_patterns:
                return None

            shot_minute = int(shot_start_time / 60)
            shot_second = int(shot_start_time % 60)

            for pattern in time_patterns:
                if abs(pattern - shot_minute) < 5 or abs(pattern - shot_second) < 10:
                    return 0.7

            return 0.2
        except Exception:
            return None

    @staticmethod
    def _score_location_match(segment_locations: List[str], shot_type: str) -> Optional[float]:
        """
        Score match based on location references.

        For now, simple heuristic: photos are better for location-specific segments.
        """
        if not segment_locations:
            return None

        if shot_type == "photo":
            return 0.6
        else:
            return 0.3

    @staticmethod
    def _generate_reasoning(
        segment: StorySegment,
        shot: MediaShot,
        text_score: float,
        time_score: Optional[float],
        location_score: Optional[float],
    ) -> str:
        """Generate human-readable reasoning for why this shot matches this segment."""
        reasons = []

        if text_score > 0.5:
            reasons.append(f"Visual content matches segment keywords (score: {text_score:.2f})")

        if time_score is not None and time_score > 0.5:
            reasons.append(f"Time reference aligns with shot timing (score: {time_score:.2f})")

        if location_score is not None and location_score > 0.5:
            reasons.append(f"Location context matches segment (score: {location_score:.2f})")

        if shot.quality_score > 0.7:
            reasons.append(f"High visual quality (score: {shot.quality_score:.2f})")

        if not reasons:
            reasons.append("Candidate shot for this segment")

        return "; ".join(reasons)

    @staticmethod
    def _persist_candidates(project_id: str, candidates: List[AlignmentCandidate]) -> None:
        """Persist alignment candidates to database."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            for candidate in candidates:
                candidate_record = AlignmentCandidateRecord(
                    candidate_id=candidate.candidate_id,
                    project_id=project_id,
                    segment_id=candidate.segment_id,
                    shot_id=candidate.shot_id,
                    match_score=candidate.match_score,
                    text_match_score=candidate.text_match_score,
                    time_match_score=candidate.time_match_score,
                    location_match_score=candidate.location_match_score,
                    reasoning=candidate.reasoning,
                    created_at=datetime.utcnow(),
                )
                session.add(candidate_record)

            session.commit()
        finally:
            session.close()
