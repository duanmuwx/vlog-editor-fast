"""Story Parser module - parses travel narrative into story segments."""

import logging
import re
import json
import uuid
from typing import List, Dict
from datetime import datetime
import requests

from src.shared.types import StorySegment, StorySkeleton
from src.server.config import get_settings
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import StorySkeletonRecord, StorySegmentRecord

logger = logging.getLogger(__name__)


class StoryParser:
    """Parse travel narrative into story segments using Kimi LLM."""

    MIN_SEGMENTS = 3
    MAX_SEGMENTS = 8
    KIMI_API_URL = "https://api.moonshot.cn/v1/chat/completions"

    @staticmethod
    def parse_story(project_id: str, travel_note: str) -> StorySkeleton:
        """
        Parse travel narrative into story segments.

        Steps:
        1. Try Kimi LLM parsing
        2. Fallback to heuristic parsing if Kimi fails
        3. Validate segment count (3-8)
        4. Create StorySkeleton and persist to DB
        5. Return StorySkeleton
        """
        kimi_key = get_settings().kimi_api_key

        if kimi_key:
            try:
                segments = StoryParser._parse_with_kimi(travel_note, kimi_key)
            except Exception as e:
                logger.warning("Kimi parsing failed, falling back to heuristic parsing: %s", e)
                segments = StoryParser._fallback_parse(travel_note)
        else:
            logger.info("KIMI_API_KEY not configured, using heuristic parsing")
            segments = StoryParser._fallback_parse(travel_note)

        if not segments or len(segments) < StoryParser.MIN_SEGMENTS:
            raise ValueError(
                f"Parsing resulted in {len(segments)} segments, "
                f"but minimum {StoryParser.MIN_SEGMENTS} required"
            )

        if len(segments) > StoryParser.MAX_SEGMENTS:
            segments = segments[: StoryParser.MAX_SEGMENTS]

        skeleton = StoryParser._create_skeleton(project_id, travel_note, segments)
        StoryParser._persist_skeleton(project_id, skeleton)

        return skeleton

    @staticmethod
    def _parse_with_kimi(travel_note: str, api_key: str) -> List[StorySegment]:
        """Call Kimi LLM API to parse narrative into segments."""
        prompt = f"""请将以下旅行游记分析并拆分成3-8个故事段落。

对于每个段落，请提供：
1. 标题（简洁的段落标题）
2. 摘要（1-2句话的段落摘要）
3. 重要度（high/medium/low）
4. 关键词（提取的关键词列表）
5. 地点（提取的地点名称列表）
6. 时间参考（提取的时间表达列表）

请以JSON格式返回，结构如下：
{{
  "segments": [
    {{
      "title": "段落标题",
      "summary": "段落摘要",
      "importance": "high|medium|low",
      "keywords": ["关键词1", "关键词2"],
      "locations": ["地点1", "地点2"],
      "timestamps": ["时间1", "时间2"]
    }}
  ]
}}

游记内容：
{travel_note}"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "moonshot-v1-8k",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        }

        response = requests.post(
            StoryParser.KIMI_API_URL, json=payload, headers=headers, timeout=30
        )
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            raise ValueError("Failed to extract JSON from Kimi response")

        parsed = json.loads(json_match.group())
        segments = StoryParser._parse_kimi_response(travel_note, parsed["segments"])

        return segments

    @staticmethod
    def _parse_kimi_response(travel_note: str, kimi_segments: List[Dict]) -> List[StorySegment]:
        """Convert Kimi response into StorySegment objects."""
        segments = []
        narrative_lower = travel_note.lower()

        for seg_data in kimi_segments:
            title = seg_data.get("title", "")
            summary = seg_data.get("summary", "")

            start_idx = 0
            end_idx = len(travel_note)

            if title:
                title_lower = title.lower()
                pos = narrative_lower.find(title_lower)
                if pos >= 0:
                    start_idx = pos

            if summary:
                summary_lower = summary.lower()
                pos = narrative_lower.find(summary_lower)
                if pos >= 0:
                    end_idx = pos + len(summary)

            segment = StorySegment(
                segment_id=str(uuid.uuid4()),
                title=title,
                summary=summary,
                start_index=start_idx,
                end_index=end_idx,
                importance=seg_data.get("importance", "medium"),
                confidence=0.85,
                keywords=seg_data.get("keywords", []),
                locations=seg_data.get("locations", []),
                timestamps=seg_data.get("timestamps", []),
            )
            segments.append(segment)

        return segments

    @staticmethod
    def _fallback_parse(travel_note: str) -> List[StorySegment]:
        """Fallback heuristic-based parsing when Kimi unavailable."""
        sentences = re.split(r"[。！？\n]+", travel_note)
        sentences = [s.strip() for s in sentences if s.strip()]

        segments = []

        if len(sentences) < 5:
            segment = StorySegment(
                segment_id=str(uuid.uuid4()),
                title="旅行故事",
                summary=travel_note[:100],
                start_index=0,
                end_index=len(travel_note),
                importance="high",
                confidence=0.5,
                keywords=[],
                locations=[],
                timestamps=[],
            )
            segments.append(segment)
        else:
            segment_size = max(1, len(sentences) // StoryParser.MAX_SEGMENTS)

            for i in range(0, len(sentences), segment_size):
                if len(segments) >= StoryParser.MAX_SEGMENTS:
                    break

                chunk = sentences[i : i + segment_size]
                text = "".join(chunk)

                start_idx = travel_note.find(text)
                if start_idx < 0:
                    start_idx = 0

                end_idx = start_idx + len(text)

                segment = StorySegment(
                    segment_id=str(uuid.uuid4()),
                    title=f"段落 {len(segments) + 1}",
                    summary=text[:100],
                    start_index=start_idx,
                    end_index=end_idx,
                    importance="medium",
                    confidence=0.6,
                    keywords=[],
                    locations=[],
                    timestamps=[],
                )
                segments.append(segment)

        while len(segments) < StoryParser.MIN_SEGMENTS:
            segment = StorySegment(
                segment_id=str(uuid.uuid4()),
                title=f"段落 {len(segments) + 1}",
                summary="",
                start_index=0,
                end_index=0,
                importance="low",
                confidence=0.3,
                keywords=[],
                locations=[],
                timestamps=[],
            )
            segments.append(segment)

        return segments

    @staticmethod
    def _create_skeleton(
        project_id: str, travel_note: str, segments: List[StorySegment]
    ) -> StorySkeleton:
        """Create StorySkeleton from parsed segments."""
        skeleton_id = str(uuid.uuid4())

        total_chars = sum(seg.end_index - seg.start_index for seg in segments)
        narrative_coverage = min(1.0, total_chars / len(travel_note)) if travel_note else 0.0

        avg_confidence = (
            sum(seg.confidence for seg in segments) / len(segments) if segments else 0.0
        )

        skeleton = StorySkeleton(
            skeleton_id=skeleton_id,
            project_id=project_id,
            version=1,
            segments=segments,
            total_segments=len(segments),
            narrative_coverage=narrative_coverage,
            parsing_confidence=avg_confidence,
            status="draft",
            created_at=datetime.utcnow(),
            confirmed_at=None,
            user_edits=None,
        )

        return skeleton

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
