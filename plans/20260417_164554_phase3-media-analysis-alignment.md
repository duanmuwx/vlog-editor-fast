# Phase 3 Implementation Plan: Media Analysis & Alignment

## Context

Phase 1 established project management, input validation, and asset indexing. Phase 2 implemented story parsing and skeleton confirmation. Phase 3 builds on this foundation to implement media analysis, story-media alignment, and highlight confirmation workflow.

**Goal**: Analyze media files (videos/photos) for visual features and quality, align story segments to media using multi-modal signals, and provide a confirmation interface for users to review and select highlights.

**Why this matters**: Media alignment is the bridge between narrative structure (Phase 2) and final composition (Phase 4). High-quality alignment ensures that the selected media supports the story effectively.

---

## Architecture Overview

### New Modules

1. **MediaAnalyzer** - Analyzes videos/photos for shot detection, quality, visual features
   - Input: project_id, media files from asset index
   - Output: Shot analysis with quality scores, visual features, audio detection
   - Responsibility: Extract visual/audio features, detect shot boundaries, score quality

2. **AlignmentEngine** - Matches story segments to media using multi-modal signals
   - Input: story skeleton, media analysis results
   - Output: Alignment candidates with confidence scores
   - Responsibility: Multi-modal matching (text, visual, time, location), ranking candidates

3. **HighlightConfirmation** - Handles user confirmation and selection of highlights
   - Input: alignment candidates, user selections
   - Output: Confirmed highlight selection
   - Responsibility: Validate selections, persist decisions, track user edits

### Data Models (New)

**MediaShot** (Pydantic model in `src/shared/types.py`):
```python
class MediaShot(BaseModel):
    shot_id: str  # UUID
    file_id: str  # FK to media_files
    shot_type: str  # "video_shot", "photo"
    start_time: Optional[float]  # For videos: start time in seconds
    end_time: Optional[float]  # For videos: end time in seconds
    duration: Optional[float]  # For videos: duration in seconds
    quality_score: float  # 0.0-1.0 (clarity, stability, composition)
    has_audio: bool  # Whether shot has audio
    visual_features: Dict[str, Any]  # Scene labels, objects, people, etc.
    confidence: float  # 0.0-1.0 detection confidence
```

**MediaAnalysis** (Pydantic model):
```python
class MediaAnalysis(BaseModel):
    analysis_id: str  # UUID
    project_id: str  # FK to projects
    shots: List[MediaShot]  # All detected shots
    total_shots: int
    analysis_status: str  # "completed", "partial", "degraded"
    created_at: datetime
```

**AlignmentCandidate** (Pydantic model):
```python
class AlignmentCandidate(BaseModel):
    candidate_id: str  # UUID
    segment_id: str  # FK to story_segments
    shot_id: str  # FK to media_shots
    match_score: float  # 0.0-1.0 overall match confidence
    text_match_score: float  # Text-visual semantic match
    time_match_score: Optional[float]  # Time-based match (if metadata available)
    location_match_score: Optional[float]  # Location-based match (if metadata available)
    reasoning: str  # Why this shot matches this segment
```

**HighlightSelection** (Pydantic model):
```python
class HighlightSelection(BaseModel):
    selection_id: str  # UUID
    project_id: str  # FK to projects
    segment_id: str  # FK to story_segments
    selected_shot_id: str  # FK to media_shots
    user_confirmed: bool  # Whether user explicitly confirmed
    alternatives_available: int  # Number of other candidates
    confirmed_at: Optional[datetime]
```

### Database Schema (New Tables)

**media_shots** table:
```sql
CREATE TABLE media_shots (
    shot_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    file_id TEXT NOT NULL,
    shot_type TEXT NOT NULL,  -- "video_shot", "photo"
    start_time REAL,  -- For videos
    end_time REAL,  -- For videos
    duration REAL,  -- For videos
    quality_score REAL NOT NULL,
    has_audio BOOLEAN NOT NULL,
    visual_features TEXT,  -- JSON object
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (file_id) REFERENCES media_files(file_id)
);
```

**media_analysis** table:
```sql
CREATE TABLE media_analysis (
    analysis_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL UNIQUE,
    total_shots INTEGER NOT NULL,
    analysis_status TEXT NOT NULL,  -- "completed", "partial", "degraded"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

**alignment_candidates** table:
```sql
CREATE TABLE alignment_candidates (
    candidate_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    segment_id TEXT NOT NULL,
    shot_id TEXT NOT NULL,
    match_score REAL NOT NULL,
    text_match_score REAL NOT NULL,
    time_match_score REAL,
    location_match_score REAL,
    reasoning TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (segment_id) REFERENCES story_segments(segment_id),
    FOREIGN KEY (shot_id) REFERENCES media_shots(shot_id)
);
```

**highlight_selections** table:
```sql
CREATE TABLE highlight_selections (
    selection_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    segment_id TEXT NOT NULL UNIQUE,
    selected_shot_id TEXT NOT NULL,
    user_confirmed BOOLEAN NOT NULL,
    alternatives_available INTEGER NOT NULL,
    confirmed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (segment_id) REFERENCES story_segments(segment_id),
    FOREIGN KEY (selected_shot_id) REFERENCES media_shots(shot_id)
);
```

### API Endpoints (New)

```
POST /api/projects/{project_id}/analyze-media
  - Input: (implicit from project)
  - Output: MediaAnalysis with all detected shots
  - Side effect: Creates media_shots and media_analysis records

GET /api/projects/{project_id}/media-analysis
  - Output: MediaAnalysis with all shots

POST /api/projects/{project_id}/align-media
  - Input: (implicit from project, uses current skeleton)
  - Output: List of AlignmentCandidates for each segment
  - Side effect: Creates alignment_candidates records

GET /api/projects/{project_id}/alignment-candidates/{segment_id}
  - Output: List of AlignmentCandidates for a specific segment

POST /api/projects/{project_id}/confirm-highlights
  - Input: List of HighlightSelection (segment_id → shot_id mappings)
  - Output: HighlightSelection list (confirmed)
  - Side effect: Creates highlight_selections records, updates project status

GET /api/projects/{project_id}/highlights/current
  - Output: Current confirmed highlight selections
```

### Project Status Extension

Extend `ProjectStatus` enum in `src/shared/types.py`:
```python
class ProjectStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    STORY_PARSED = "story_parsed"
    SKELETON_CONFIRMED = "skeleton_confirmed"
    MEDIA_ANALYZED = "media_analyzed"  # NEW
    MEDIA_ALIGNED = "media_aligned"  # NEW
    HIGHLIGHTS_CONFIRMED = "highlights_confirmed"  # NEW
    RUNNING = "running"
    AWAITING_USER = "awaiting_user"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## Implementation Details

### 1. MediaAnalyzer Module (`src/server/modules/media_analyzer.py`)

**Responsibility**: Analyze videos/photos for shots, quality, and visual features

**Key Methods**:

```python
class MediaAnalyzer:
    @staticmethod
    def analyze_media(project_id: str) -> MediaAnalysis:
        """
        Analyze all media files in project.
        
        Steps:
        1. Retrieve all media files from asset index
        2. For each video: detect shot boundaries, extract frames, score quality
        3. For each photo: score quality, extract visual features
        4. Aggregate results into MediaAnalysis
        5. Persist to database
        6. Return MediaAnalysis
        """
        
    @staticmethod
    def _analyze_video(project_id: str, file_id: str, file_path: str) -> List[MediaShot]:
        """
        Analyze video file for shots.
        
        Steps:
        1. Open video with OpenCV
        2. Detect shot boundaries using frame difference
        3. For each shot: extract keyframe, score quality
        4. Detect audio presence
        5. Extract visual features from keyframe
        6. Return list of MediaShot objects
        """
        
    @staticmethod
    def _analyze_photo(project_id: str, file_id: str, file_path: str) -> MediaShot:
        """
        Analyze photo file.
        
        Steps:
        1. Load photo with PIL
        2. Score quality (sharpness, brightness, composition)
        3. Extract visual features (scene labels, objects)
        4. Return MediaShot object
        """
        
    @staticmethod
    def _detect_shot_boundaries(video_path: str, threshold: float = 30.0) -> List[Tuple[float, float]]:
        """Detect shot boundaries using frame difference"""
        
    @staticmethod
    def _score_quality(frame_or_image) -> float:
        """Score visual quality (0.0-1.0)"""
        
    @staticmethod
    def _extract_visual_features(frame_or_image) -> Dict[str, Any]:
        """Extract visual features (scene labels, objects, people)"""
        
    @staticmethod
    def _persist_analysis(project_id: str, analysis: MediaAnalysis) -> None:
        """Persist analysis results to database"""
```

**Implementation Strategy**:
- Use OpenCV for video shot detection (frame difference > threshold)
- Use PIL for photo analysis
- Score quality based on: sharpness (Laplacian variance), brightness, composition
- Extract visual features using simple heuristics (color histograms, edge detection)
- Handle missing/corrupted files gracefully
- Support degraded mode (skip complex analysis if resources limited)

### 2. AlignmentEngine Module (`src/server/modules/alignment_engine.py`)

**Responsibility**: Match story segments to media using multi-modal signals

**Key Methods**:

```python
class AlignmentEngine:
    @staticmethod
    def align_media(project_id: str, skeleton_id: str) -> List[AlignmentCandidate]:
        """
        Align story segments to media shots.
        
        Steps:
        1. Retrieve story skeleton and segments
        2. Retrieve media analysis (shots)
        3. For each segment: generate candidate shots
        4. Score each candidate using multi-modal signals
        5. Rank candidates by score
        6. Persist to database
        7. Return all candidates
        """
        
    @staticmethod
    def _generate_candidates(segment: StorySegment, shots: List[MediaShot]) -> List[AlignmentCandidate]:
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
        
    @staticmethod
    def _score_text_match(segment_summary: str, visual_features: Dict) -> float:
        """Score semantic match between text and visual features"""
        
    @staticmethod
    def _score_time_match(segment_timestamps: List[str], shot_time: Optional[float]) -> Optional[float]:
        """Score match based on time references"""
        
    @staticmethod
    def _score_location_match(segment_locations: List[str], photo_exif: Optional[Dict]) -> Optional[float]:
        """Score match based on location references"""
        
    @staticmethod
    def _persist_candidates(project_id: str, candidates: List[AlignmentCandidate]) -> None:
        """Persist alignment candidates to database"""
```

**Implementation Strategy**:
- Text-visual match: Simple keyword matching (segment keywords vs. visual feature labels)
- Time match: Parse segment timestamps, compare with shot time ranges
- Location match: Extract GPS from EXIF, compare with segment locations
- Combine scores: text_score * 0.6 + time_score * 0.2 + location_score * 0.2
- Fallback: If metadata missing, use text-visual match only
- Generate 3-5 candidates per segment (top N by score)

### 3. HighlightConfirmation Module (`src/server/modules/highlight_confirmation.py`)

**Responsibility**: Handle user confirmation and selection of highlights

**Key Methods**:

```python
class HighlightConfirmation:
    @staticmethod
    def confirm_highlights(project_id: str, selections: List[Dict]) -> List[HighlightSelection]:
        """
        Confirm user's highlight selections.
        
        Steps:
        1. Validate selections (all segments have selection, valid shot_ids)
        2. For each selection: create HighlightSelection record
        3. Persist to database
        4. Update project status to "highlights_confirmed"
        5. Return confirmed selections
        """
        
    @staticmethod
    def _validate_selections(project_id: str, skeleton_id: str, selections: List[Dict]) -> Tuple[bool, str]:
        """Validate that all segments have valid selections"""
        
    @staticmethod
    def _persist_selections(project_id: str, selections: List[HighlightSelection]) -> None:
        """Persist highlight selections to database"""
        
    @staticmethod
    def get_current_highlights(project_id: str) -> Optional[List[HighlightSelection]]:
        """Retrieve current confirmed highlight selections"""
```

**Implementation Strategy**:
- Validate: All segments must have exactly one selection
- Validate: Selected shot_id must exist in alignment_candidates for that segment
- Track: Number of alternatives available for each segment
- Persist: Record user_confirmed=True for explicit confirmations
- Support: User can replace selections before final confirmation

### 4. API Routes (`src/server/api/projects.py` - extend)

```python
@router.post("/projects/{project_id}/analyze-media")
async def analyze_media(project_id: str):
    """Analyze media files for shots and quality"""
    # 1. Get project config
    # 2. Call MediaAnalyzer.analyze_media()
    # 3. Update project status to "media_analyzed"
    # 4. Return MediaAnalysis

@router.get("/projects/{project_id}/media-analysis")
async def get_media_analysis(project_id: str):
    """Retrieve media analysis results"""
    # 1. Query media_analysis record
    # 2. Query all media_shots
    # 3. Return MediaAnalysis

@router.post("/projects/{project_id}/align-media")
async def align_media(project_id: str):
    """Align story segments to media"""
    # 1. Get current skeleton
    # 2. Get media analysis
    # 3. Call AlignmentEngine.align_media()
    # 4. Update project status to "media_aligned"
    # 5. Return alignment candidates

@router.get("/projects/{project_id}/alignment-candidates/{segment_id}")
async def get_alignment_candidates(project_id: str, segment_id: str):
    """Get alignment candidates for a segment"""
    # 1. Query alignment_candidates for segment
    # 2. Return sorted by match_score

@router.post("/projects/{project_id}/confirm-highlights")
async def confirm_highlights(project_id: str, request: HighlightConfirmationRequest):
    """Confirm highlight selections"""
    # 1. Call HighlightConfirmation.confirm_highlights()
    # 2. Update project status to "highlights_confirmed"
    # 3. Return confirmed selections

@router.get("/projects/{project_id}/highlights/current")
async def get_current_highlights(project_id: str):
    """Get current confirmed highlights"""
    # 1. Call HighlightConfirmation.get_current_highlights()
    # 2. Return selections
```

### 5. Database Schema Updates (`src/server/storage/schemas.py`)

Add SQLAlchemy ORM models:
- `MediaShotRecord`
- `MediaAnalysisRecord`
- `AlignmentCandidateRecord`
- `HighlightSelectionRecord`

Update `Database` class to create new tables on initialization.

### 6. Tests

**Unit Tests** (`tests/unit/test_media_analyzer.py`):
- `test_analyze_video_shot_detection()` - Detect shot boundaries
- `test_analyze_photo_quality()` - Score photo quality
- `test_extract_visual_features()` - Extract visual features
- `test_analyze_media_complete()` - Full analysis workflow

**Unit Tests** (`tests/unit/test_alignment_engine.py`):
- `test_align_media_text_match()` - Text-visual matching
- `test_align_media_time_match()` - Time-based matching
- `test_align_media_location_match()` - Location-based matching
- `test_align_media_fallback()` - Fallback when metadata missing
- `test_generate_candidates()` - Candidate generation

**Unit Tests** (`tests/unit/test_highlight_confirmation.py`):
- `test_confirm_highlights_valid()` - Valid selections
- `test_confirm_highlights_invalid()` - Invalid selections
- `test_confirm_highlights_persistence()` - Database persistence

**Integration Tests** (`tests/integration/test_phase3_flow.py`):
- `test_complete_phase3_flow()` - Analyze → Align → Confirm
- `test_phase3_with_metadata()` - With EXIF/GPS data
- `test_phase3_without_metadata()` - Fallback mode
- `test_phase3_insufficient_media()` - Degraded mode

---

## Files to Create/Modify

### New Files
- `src/shared/types.py` - Add MediaShot, MediaAnalysis, AlignmentCandidate, HighlightSelection models
- `src/server/modules/media_analyzer.py` - MediaAnalyzer implementation
- `src/server/modules/alignment_engine.py` - AlignmentEngine implementation
- `src/server/modules/highlight_confirmation.py` - HighlightConfirmation implementation
- `tests/unit/test_media_analyzer.py` - Unit tests for MediaAnalyzer
- `tests/unit/test_alignment_engine.py` - Unit tests for AlignmentEngine
- `tests/unit/test_highlight_confirmation.py` - Unit tests for HighlightConfirmation
- `tests/integration/test_phase3_flow.py` - Integration tests

### Modified Files
- `src/shared/types.py` - Add ProjectStatus enum values (MEDIA_ANALYZED, MEDIA_ALIGNED, HIGHLIGHTS_CONFIRMED)
- `src/server/storage/schemas.py` - Add ORM models for media analysis tables
- `src/server/storage/database.py` - Update table creation logic
- `src/server/api/projects.py` - Add Phase 3 endpoints
- `requirements.txt` - Add dependencies (opencv-python, pillow already present)

---

## Implementation Sequence

1. **Data Models** - Define Pydantic models in `src/shared/types.py`
2. **Database Schema** - Add ORM models and update database initialization
3. **MediaAnalyzer Module** - Implement media analysis logic
4. **AlignmentEngine Module** - Implement alignment logic
5. **HighlightConfirmation Module** - Implement confirmation logic
6. **API Routes** - Add Phase 3 endpoints
7. **Unit Tests** - Test each module independently
8. **Integration Tests** - Test complete Phase 3 workflow

---

## Verification & Testing

### Manual Testing
1. Create a project with travel narrative and media
2. Call `POST /api/projects/{project_id}/analyze-media` → Verify shots are detected
3. Call `POST /api/projects/{project_id}/align-media` → Verify candidates are generated
4. Call `POST /api/projects/{project_id}/confirm-highlights` → Verify selections are confirmed
5. Call `GET /api/projects/{project_id}/highlights/current` → Verify confirmed highlights are returned

### Automated Testing
- Run `pytest tests/unit/test_media_analyzer.py -v`
- Run `pytest tests/unit/test_alignment_engine.py -v`
- Run `pytest tests/unit/test_highlight_confirmation.py -v`
- Run `pytest tests/integration/test_phase3_flow.py -v`
- Verify all tests pass and coverage > 80%

### Integration with Phase 1 & 2
- Verify Phase 1 & 2 tests still pass
- Verify project status transitions correctly (skeleton_confirmed → media_analyzed → media_aligned → highlights_confirmed)
- Verify database schema is backward compatible

---

## Key Design Decisions

1. **Shot Detection Strategy**: Use frame difference for video shot detection (simple, fast, effective)
2. **Quality Scoring**: Combine sharpness, brightness, composition into single 0.0-1.0 score
3. **Multi-modal Alignment**: Weighted combination of text, time, and location signals
4. **Fallback Strategy**: When metadata missing, use text-visual match only
5. **Candidate Generation**: Generate 3-5 candidates per segment for user choice
6. **User Confirmation**: Require explicit confirmation of all highlights before proceeding

---

## Critical Implementation Notes

### MediaAnalyzer
- Use OpenCV for video processing (already in requirements)
- Implement shot boundary detection using frame difference
- Score quality based on: Laplacian variance (sharpness), brightness, edge density
- Extract visual features using simple heuristics (color histograms, edge detection)
- Handle corrupted files gracefully (skip, log warning)
- Support degraded mode (skip complex analysis if resources limited)

### AlignmentEngine
- Text-visual match: Simple keyword matching (segment keywords vs. visual feature labels)
- Time match: Parse segment timestamps, compare with shot time ranges
- Location match: Extract GPS from EXIF, compare with segment locations
- Combine scores with weights: text * 0.6 + time * 0.2 + location * 0.2
- Fallback: If metadata missing, use text-visual match only
- Generate 3-5 candidates per segment (top N by score)

### HighlightConfirmation
- Validate: All segments must have exactly one selection
- Validate: Selected shot_id must exist in alignment_candidates
- Track: Number of alternatives available for each segment
- Persist: Record user_confirmed=True for explicit confirmations
- Support: User can replace selections before final confirmation

---

## User Decisions (Confirmed)

1. **Shot Detection Strategy**: Hybrid Approach
   - Use frame difference for fast detection (threshold: 30.0)
   - Use histogram comparison for robustness to gradual transitions
   - Combine both signals for better accuracy
   - Implementation: If frame_diff > threshold OR histogram_diff > threshold, mark as shot boundary

2. **Quality Scoring Method**: Hybrid Approach
   - Use simple heuristics (Laplacian variance, brightness, edge density) for quick scoring
   - Use ML-based scoring for high-importance segments (importance="high")
   - Fallback to heuristics if ML model unavailable
   - Implementation: Quick heuristic pass first, then ML refinement for important segments

3. **Alignment Scoring Weights**: Text-Heavy
   - Text-visual match: 60% (primary signal for travel vlogs)
   - Time-based match: 20% (secondary signal)
   - Location-based match: 20% (tertiary signal)
   - Formula: final_score = text_score * 0.6 + time_score * 0.2 + location_score * 0.2

4. **Candidate Count**: Balanced (5 candidates per segment)
   - Generate 5 candidates per segment
   - Good balance between user choice and performance
   - Rank by match_score, return top 5

5. **Fallback Strategy**: Hybrid with Warnings
   - Use text-visual matching when metadata is missing
   - Warn user about reduced confidence when metadata unavailable
   - Track metadata availability in alignment results
   - Implementation: Set time_match_score=None and location_match_score=None when metadata missing, display warning
