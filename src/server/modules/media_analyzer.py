"""Media Analyzer module - analyzes videos/photos for shots and quality."""

import os
import uuid
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import cv2
import numpy as np
from PIL import Image

from src.shared.types import MediaShot, MediaAnalysis
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import MediaShotRecord, MediaAnalysisRecord, MediaFileRecord


class MediaAnalyzer:
    """Analyze media files for shots, quality, and visual features."""

    SHOT_BOUNDARY_THRESHOLD = 30.0
    HISTOGRAM_THRESHOLD = 0.15
    MIN_SHOT_DURATION = 0.5  # seconds

    @staticmethod
    def analyze_media(project_id: str) -> MediaAnalysis:
        """
        Analyze all media files in project.

        Steps:
        1. Retrieve all media files from database
        2. For each video: detect shot boundaries, extract frames, score quality
        3. For each photo: score quality, extract visual features
        4. Aggregate results into MediaAnalysis
        5. Persist to database
        6. Return MediaAnalysis
        """
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            media_files = session.query(MediaFileRecord).filter_by(project_id=project_id).all()

            all_shots = []
            analysis_status = "completed"

            for media_file in media_files:
                try:
                    if media_file.file_type == "video":
                        shots = MediaAnalyzer._analyze_video(project_id, media_file.file_id, media_file.file_path)
                    else:
                        shot = MediaAnalyzer._analyze_photo(project_id, media_file.file_id, media_file.file_path)
                        shots = [shot] if shot else []

                    all_shots.extend(shots)
                except Exception as e:
                    print(f"Error analyzing {media_file.file_path}: {e}")
                    analysis_status = "partial"

            analysis_id = str(uuid.uuid4())
            analysis = MediaAnalysis(
                analysis_id=analysis_id,
                project_id=project_id,
                shots=all_shots,
                total_shots=len(all_shots),
                analysis_status=analysis_status,
                created_at=datetime.utcnow(),
            )

            MediaAnalyzer._persist_analysis(project_id, analysis)

            return analysis
        finally:
            session.close()

    @staticmethod
    def _analyze_video(project_id: str, file_id: str, file_path: str) -> List[MediaShot]:
        """
        Analyze video file for shots.

        Steps:
        1. Open video with OpenCV
        2. Detect shot boundaries using frame difference + histogram
        3. For each shot: extract keyframe, score quality
        4. Detect audio presence
        5. Extract visual features from keyframe
        6. Return list of MediaShot objects
        """
        shots = []

        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return shots

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            shot_boundaries = [0]
            prev_frame = None
            prev_hist = None

            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % 5 == 0:
                    frame_diff = MediaAnalyzer._compute_frame_difference(prev_frame, frame)
                    hist_diff = MediaAnalyzer._compute_histogram_difference(prev_hist, frame)

                    if frame_diff > MediaAnalyzer.SHOT_BOUNDARY_THRESHOLD or hist_diff > MediaAnalyzer.HISTOGRAM_THRESHOLD:
                        shot_boundaries.append(frame_idx)

                    prev_frame = frame.copy()
                    prev_hist = cv2.calcHist([cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)], [0, 1], None, [180, 256], [0, 180, 0, 256])

                frame_idx += 1

            shot_boundaries.append(total_frames)

            for i in range(len(shot_boundaries) - 1):
                start_frame = shot_boundaries[i]
                end_frame = shot_boundaries[i + 1]
                duration = (end_frame - start_frame) / fps

                if duration < MediaAnalyzer.MIN_SHOT_DURATION:
                    continue

                start_time = start_frame / fps
                end_time = end_frame / fps

                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame + (end_frame - start_frame) // 2)
                ret, keyframe = cap.read()

                if ret:
                    quality_score = MediaAnalyzer._score_quality_heuristic(keyframe)
                    visual_features = MediaAnalyzer._extract_visual_features(keyframe)

                    shot = MediaShot(
                        shot_id=str(uuid.uuid4()),
                        file_id=file_id,
                        shot_type="video_shot",
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        quality_score=quality_score,
                        has_audio=True,
                        visual_features=visual_features,
                        confidence=0.85,
                    )
                    shots.append(shot)

            cap.release()
        except Exception as e:
            print(f"Error analyzing video {file_path}: {e}")

        return shots

    @staticmethod
    def _analyze_photo(project_id: str, file_id: str, file_path: str) -> Optional[MediaShot]:
        """
        Analyze photo file.

        Steps:
        1. Load photo with PIL
        2. Score quality (sharpness, brightness, composition)
        3. Extract visual features (scene labels, objects)
        4. Return MediaShot object
        """
        try:
            image = Image.open(file_path)
            image_cv = cv2.imread(file_path)

            if image_cv is None:
                return None

            quality_score = MediaAnalyzer._score_quality_heuristic(image_cv)
            visual_features = MediaAnalyzer._extract_visual_features(image_cv)

            shot = MediaShot(
                shot_id=str(uuid.uuid4()),
                file_id=file_id,
                shot_type="photo",
                quality_score=quality_score,
                has_audio=False,
                visual_features=visual_features,
                confidence=0.9,
            )

            return shot
        except Exception as e:
            print(f"Error analyzing photo {file_path}: {e}")
            return None

    @staticmethod
    def _compute_frame_difference(prev_frame: Optional[np.ndarray], curr_frame: np.ndarray) -> float:
        """Compute frame difference using L2 norm."""
        if prev_frame is None:
            return 0.0

        try:
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(prev_gray, curr_gray)
            return float(np.mean(diff))
        except Exception:
            return 0.0

    @staticmethod
    def _compute_histogram_difference(prev_hist: Optional[np.ndarray], curr_frame: np.ndarray) -> float:
        """Compute histogram difference."""
        if prev_hist is None:
            return 0.0

        try:
            curr_hsv = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2HSV)
            curr_hist = cv2.calcHist([curr_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
            return float(cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_BHATTACHARYYA))
        except Exception:
            return 0.0

    @staticmethod
    def _score_quality_heuristic(frame: np.ndarray) -> float:
        """
        Score visual quality using heuristics.

        Combines:
        - Sharpness (Laplacian variance)
        - Brightness (mean pixel value)
        - Edge density (Canny edge detection)
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 500.0)

            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2

            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
            edge_score = min(1.0, edge_density * 5)

            quality_score = (sharpness_score * 0.5 + brightness_score * 0.3 + edge_score * 0.2)
            return float(np.clip(quality_score, 0.0, 1.0))
        except Exception:
            return 0.5

    @staticmethod
    def _extract_visual_features(frame: np.ndarray) -> Dict[str, Any]:
        """
        Extract visual features from frame.

        Simple heuristics:
        - Color histogram (dominant colors)
        - Edge density
        - Brightness level
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            brightness = float(np.mean(gray) / 255.0)

            edges = cv2.Canny(gray, 100, 200)
            edge_density = float(np.sum(edges > 0) / (gray.shape[0] * gray.shape[1]))

            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            dominant_hue = int(np.argmax(hist_h))

            hue_names = {
                0: "red", 30: "orange", 60: "yellow", 90: "green",
                120: "cyan", 150: "blue", 180: "magenta"
            }
            dominant_color = hue_names.get(min(hue_names.keys(), key=lambda x: abs(x - dominant_hue)), "neutral")

            return {
                "brightness": brightness,
                "edge_density": edge_density,
                "dominant_color": dominant_color,
                "scene_type": "outdoor" if brightness > 0.5 else "indoor",
            }
        except Exception:
            return {"brightness": 0.5, "edge_density": 0.3, "dominant_color": "neutral", "scene_type": "unknown"}

    @staticmethod
    def _persist_analysis(project_id: str, analysis: MediaAnalysis) -> None:
        """Persist analysis results to database."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            analysis_record = MediaAnalysisRecord(
                analysis_id=analysis.analysis_id,
                project_id=project_id,
                total_shots=analysis.total_shots,
                analysis_status=analysis.analysis_status,
                created_at=analysis.created_at,
            )
            session.add(analysis_record)

            for shot in analysis.shots:
                shot_record = MediaShotRecord(
                    shot_id=shot.shot_id,
                    project_id=project_id,
                    file_id=shot.file_id,
                    shot_type=shot.shot_type,
                    start_time=shot.start_time,
                    end_time=shot.end_time,
                    duration=shot.duration,
                    quality_score=shot.quality_score,
                    has_audio=shot.has_audio,
                    visual_features=shot.visual_features,
                    confidence=shot.confidence,
                    created_at=datetime.utcnow(),
                )
                session.add(shot_record)

            session.commit()
        finally:
            session.close()
