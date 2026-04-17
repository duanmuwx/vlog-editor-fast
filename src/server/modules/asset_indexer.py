"""Asset Indexer module."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None
    TAGS = None

from src.shared.types import AssetIndex, MediaFileInfo, FileType
from src.server.storage.database import get_or_create_db
from src.server.storage.schemas import MediaFileRecord, AssetIndexRecord


class AssetIndexer:
    """Indexes media assets."""

    @staticmethod
    def index_assets(project_id: str, media_files: list) -> AssetIndex:
        """Generate complete asset index."""
        db = get_or_create_db(project_id)
        session = db.get_session()

        try:
            media_items = []
            total_videos = 0
            total_photos = 0
            total_duration = 0.0
            metadata_availability = {
                'exif': 0,
                'gps': 0,
                'timestamp': 0,
                'audio': 0
            }

            for file_path in media_files:
                if not os.path.exists(file_path):
                    continue

                ext = Path(file_path).suffix.lower()
                file_type = AssetIndexer._determine_file_type(ext)

                if file_type == FileType.VIDEO:
                    total_videos += 1
                    metadata = AssetIndexer.extract_video_metadata(file_path)
                    if metadata.duration:
                        total_duration += metadata.duration
                    if metadata.has_audio:
                        metadata_availability['audio'] += 1
                elif file_type == FileType.PHOTO:
                    total_photos += 1
                    metadata = AssetIndexer.extract_photo_metadata(file_path)
                    if metadata.exif_data:
                        metadata_availability['exif'] += 1
                        if 'gps' in metadata.exif_data:
                            metadata_availability['gps'] += 1
                        if 'datetime' in metadata.exif_data:
                            metadata_availability['timestamp'] += 1
                else:
                    continue

                media_items.append(metadata)

                # Save to database
                file_record = MediaFileRecord(
                    file_id=str(uuid.uuid4()),
                    project_id=project_id,
                    file_path=file_path,
                    file_type=file_type.value,
                    file_size=os.path.getsize(file_path),
                    duration=metadata.duration,
                    resolution=f"{metadata.resolution[0]}x{metadata.resolution[1]}" if metadata.resolution else None,
                    creation_time=metadata.creation_time,
                    has_audio=metadata.has_audio,
                    exif_data=metadata.exif_data,
                    indexed_at=datetime.utcnow()
                )
                session.add(file_record)

            # Normalize metadata availability to percentages
            total_files = total_videos + total_photos
            if total_files > 0:
                metadata_availability = {
                    k: v / total_files for k, v in metadata_availability.items()
                }

            # Create asset index
            asset_index = AssetIndex(
                project_id=project_id,
                total_videos=total_videos,
                total_photos=total_photos,
                total_duration=total_duration,
                indexed_at=datetime.utcnow(),
                media_items=media_items,
                metadata_availability=metadata_availability
            )

            # Save to database
            index_record = AssetIndexRecord(
                index_id=str(uuid.uuid4()),
                project_id=project_id,
                total_videos=total_videos,
                total_photos=total_photos,
                total_duration=total_duration,
                metadata_availability=metadata_availability,
                indexed_at=datetime.utcnow()
            )
            session.add(index_record)
            session.commit()

            return asset_index
        finally:
            session.close()

    @staticmethod
    def extract_video_metadata(file_path: str) -> MediaFileInfo:
        """Extract video metadata."""
        duration = None
        resolution = None
        has_audio = False

        if cv2:
            try:
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    if fps > 0:
                        duration = frame_count / fps
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    if width > 0 and height > 0:
                        resolution = (width, height)
                    cap.release()
            except Exception:
                pass

        # Try to detect audio (simplified)
        has_audio = True  # placeholder

        return MediaFileInfo(
            file_path=file_path,
            file_type=FileType.VIDEO,
            file_size=os.path.getsize(file_path),
            duration=duration,
            resolution=resolution,
            creation_time=datetime.fromtimestamp(os.path.getctime(file_path)),
            has_audio=has_audio,
            exif_data=None
        )

    @staticmethod
    def extract_photo_metadata(file_path: str) -> MediaFileInfo:
        """Extract photo metadata."""
        resolution = None
        creation_time = None
        exif_data = {}

        if Image:
            try:
                img = Image.open(file_path)
                resolution = img.size

                # Extract EXIF data
                exif_dict = img._getexif() if hasattr(img, '_getexif') else None
                if exif_dict:
                    for tag_id, value in exif_dict.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        exif_data[tag_name] = str(value)[:100]  # limit value length

                # Try to get datetime from EXIF
                if 'DateTime' in exif_data:
                    try:
                        creation_time = datetime.strptime(exif_data['DateTime'], '%Y:%m:%d %H:%M:%S')
                    except Exception:
                        pass
            except Exception:
                pass

        if not creation_time:
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))

        return MediaFileInfo(
            file_path=file_path,
            file_type=FileType.PHOTO,
            file_size=os.path.getsize(file_path),
            duration=None,
            resolution=resolution,
            creation_time=creation_time,
            has_audio=False,
            exif_data=exif_data if exif_data else None
        )

    @staticmethod
    def _determine_file_type(ext: str) -> Optional[FileType]:
        """Determine file type from extension."""
        video_formats = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'}
        photo_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

        if ext in video_formats:
            return FileType.VIDEO
        elif ext in photo_formats:
            return FileType.PHOTO
        return None
