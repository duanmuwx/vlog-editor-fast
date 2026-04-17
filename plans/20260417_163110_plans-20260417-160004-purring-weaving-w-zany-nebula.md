# Phase 2 Implementation Plan: Story Analysis & Confirmation

## Context

Phase 1 established the infrastructure for project management, input validation, and media asset indexing. Phase 2 builds on this foundation to implement story analysis and user confirmation workflow.

**Goal**: Parse the travel narrative into story segments (3-8 segments), generate a story skeleton, and provide a confirmation interface where users can review, modify, and freeze the skeleton before proceeding to media alignment.

**Why this matters**: The story structure is the organizing principle for the entire system. A well-structured skeleton ensures that media alignment, highlight selection, and final composition all follow a coherent narrative arc.

---

## Architecture Overview

### New Modules

1. **StoryParser** - Parses travel narrative into story segments
   - Input: travel_note (text), project_id
   - Output: List of story segments with summaries, time indices, importance scores
   - Fallback: When narrative is too short or unstructured, use simplified parsing

2. **StorySkeleton** - Generates skeleton from parsed segments
   - Input: story segments, project metadata
   - Output: Frozen story skeleton with versioning
   - Responsibility: Aggregate segments, assign IDs, create version record

3. **SkeletonConfirmation** - Handles user confirmation workflow
   - Input: skeleton_id, user edits (merge, delete, reorder, mark)
   - Output: Confirmed skeleton version
   - Responsibility: Validate edits, update skeleton, persist decisions

### Data Models (New)

**StorySegment** (Pydantic model in `src/shared/types.py`):
```python
class StorySegment(BaseModel):
    segment_id: str  # UUID
    title: str  # Auto-generated title
    summary: str  # 1-2 sentence summary
    start_index: int  # Character index in narrative
    end_index: int  # Character index in narrative
    importance: str  # "high", "medium", "low"
    confidence: float  # 0.0-1.0 parsing confidence
    keywords: List[str]  # Extracted keywords
    locations: List[str]  # Extracted location names
    timestamps: List[str]  # Extracted time references
```

**StorySkeleton** (Pydantic model):
```python
class StorySkeleton(BaseModel):
    skeleton_id: str  # UUID
    project_id: str  # FK to projects
    version: int  # Version number (starts at 1)
    segments: List[StorySegment]  # Ordered list
    total_segments: int
    narrative_coverage: float  # % of narrative covered
    parsing_confidence: float  # Average confidence
    status: str  # "draft", "confirmed"
    created_at: datetime
    confirmed_at: Optional[datetime]
    user_edits: Optional[Dict]  # Track user modifications
```

**SkeletonConfirmationRequest** (Pydantic model):
```python
class SkeletonConfirmationRequest(BaseModel):
    skeleton_id: str
    edits: List[Dict]  # List of edit operations
    # Each edit: {"operation": "merge|delete|reorder|mark", "segment_ids": [...], "payload": {...}}
```

### Database Schema (New Tables)

**story_segments** table:
```sql
CREATE TABLE story_segments (
    segment_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    skeleton_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    start_index INTEGER NOT NULL,
    end_index INTEGER NOT NULL,
    importance TEXT NOT NULL,
    confidence REAL NOT NULL,
    keywords TEXT,  -- JSON array
    locations TEXT,  -- JSON array
    timestamps TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (skeleton_id) REFERENCES story_skeletons(skeleton_id)
);
```

**story_skeletons** table:
```sql
CREATE TABLE story_skeletons (
    skeleton_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL UNIQUE,
    version INTEGER NOT NULL,
    total_segments INTEGER NOT NULL,
    narrative_coverage REAL NOT NULL,
    parsing_confidence REAL NOT NULL,
    status TEXT NOT NULL,  -- "draft", "confirmed"
    user_edits TEXT,  -- JSON object tracking modifications
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

**skeleton_confirmations** table:
```sql
CREATE TABLE skeleton_confirmations (
    confirmation_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    skeleton_id TEXT NOT NULL,
    edits TEXT NOT NULL,  -- JSON array of edit operations
    confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (skeleton_id) REFERENCES story_skeletons(skeleton_id)
);
```

### API Endpoints (New)

```
POST /api/projects/{project_id}/story/parse
  - Input: (implicit from project config)
  - Output: StorySkeleton (draft status)
  - Side effect: Creates story_skeletons and story_segments records

GET /api/projects/{project_id}/skeleton/{skeleton_id}
  - Output: StorySkeleton with all segments

POST /api/projects/{project_id}/skeleton/{skeleton_id}/confirm
  - Input: SkeletonConfirmationRequest (edits)
  - Output: StorySkeleton (confirmed status)
  - Side effect: Updates skeleton status, creates skeleton_confirmations record

GET /api/projects/{project_id}/skeleton/current
  - Output: Latest confirmed skeleton (or draft if none confirmed)
```

### Project Status Extension

Extend `ProjectStatus` enum in `src/shared/types.py`:
```python
class ProjectStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    STORY_PARSED = "story_parsed"  # NEW
    SKELETON_CONFIRMED = "skeleton_confirmed"  # NEW
    RUNNING = "running"
    AWAITING_USER = "awaiting_user"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## Implementation Details

### 1. StoryParser Module (`src/server/modules/story_parser.py`)

**Responsibility**: Parse travel narrative into story segments using Kimi LLM

**Key Methods**:

```python
class StoryParser:
    @staticmethod
    def parse_story(project_id: str, travel_note: str) -> StorySkeleton:
        """
        Parse travel narrative into story segments using Kimi LLM.
        
        Steps:
        1. Call Kimi API with structured prompt to parse narrative
        2. Extract segments from Kimi response
        3. Validate segment count (3-8)
        4. Calculate confidence scores
        5. Create StorySkeleton and persist to DB
        
        Fallback: If Kimi unavailable, use simple heuristic-based parsing
        """
        
    @staticmethod
    def _call_kimi_api(travel_note: str) -> Dict:
        """
        Call Kimi LLM API with structured prompt.
        
        Prompt instructs Kimi to:
        - Parse narrative into 3-8 story segments
        - For each segment: title, summary, importance (high/medium/low)
        - Extract: keywords, locations, time references
        - Return JSON with structured output
        """
        
    @staticmethod
    def _parse_kimi_response(response: Dict) -> List[StorySegment]:
        """Parse Kimi response into StorySegment objects"""
        
    @staticmethod
    def _fallback_parse(travel_note: str) -> List[StorySegment]:
        """
        Fallback heuristic-based parsing when Kimi unavailable.
        
        Steps:
        1. Split text into sentences/paragraphs
        2. Extract locations and time references
        3. Cluster by topic/location/time
        4. Generate summaries
        5. Score importance
        """
        
    @staticmethod
    def _extract_entities(text: str) -> Dict:
        """Extract locations, timestamps, keywords using regex"""
        
    @staticmethod
    def _cluster_segments(sentences: List[str], entities: Dict) -> List[Dict]:
        """Cluster sentences into 3-8 segments"""
```

**Implementation Strategy**:
- Primary: Use Kimi LLM for high-quality parsing
- Fallback: Simple heuristic-based parsing if Kimi API fails or key not configured
- Always output confidence scores (from Kimi or estimated from fallback)
- Validate segment count is 3-8; reject if outside range
- Handle API errors gracefully with informative error messages

### 2. StorySkeleton Module (`src/server/modules/story_skeleton.py`)

**Responsibility**: Generate and manage story skeleton versions

**Key Methods**:

```python
class StorySkeleton:
    @staticmethod
    def generate_skeleton(project_id: str, story_segments: List[StorySegment]) -> StorySkeleton:
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
        
    @staticmethod
    def get_skeleton(project_id: str, skeleton_id: str) -> StorySkeleton:
        """Retrieve skeleton and all segments from DB"""
        
    @staticmethod
    def get_current_skeleton(project_id: str) -> Optional[StorySkeleton]:
        """Get latest confirmed skeleton, or draft if none confirmed"""
```

**Implementation Strategy**:
- Assign UUIDs to skeleton and segments
- Calculate coverage as (total_chars_in_segments / total_chars_in_narrative)
- Calculate confidence as average of segment confidences
- Persist immediately to DB

### 3. SkeletonConfirmation Module (`src/server/modules/skeleton_confirmation.py`)

**Responsibility**: Handle user confirmation and edits

**Key Methods**:

```python
class SkeletonConfirmation:
    @staticmethod
    def confirm_skeleton(project_id: str, skeleton_id: str, edits: List[Dict]) -> StorySkeleton:
        """
        Apply user edits and confirm skeleton.
        
        Supported edits:
        - merge: Combine multiple segments into one
        - delete: Remove a segment
        - reorder: Change segment order
        - mark: Mark segment as "must_keep" or "optional"
        
        Steps:
        1. Validate edits (no orphaned segments, valid operations)
        2. Apply edits to skeleton
        3. Recalculate coverage and confidence
        4. Update skeleton status to "confirmed"
        5. Create skeleton_confirmations record
        6. Update project status to "skeleton_confirmed"
        7. Return confirmed skeleton
        """
        
    @staticmethod
    def _validate_edits(skeleton: StorySkeleton, edits: List[Dict]) -> Tuple[bool, str]:
        """Validate edit operations"""
        
    @staticmethod
    def _apply_merge(segments: List[StorySegment], segment_ids: List[str]) -> StorySegment:
        """Merge multiple segments into one"""
        
    @staticmethod
    def _apply_delete(segments: List[StorySegment], segment_ids: List[str]) -> List[StorySegment]:
        """Remove segments"""
        
    @staticmethod
    def _apply_reorder(segments: List[StorySegment], new_order: List[str]) -> List[StorySegment]:
        """Reorder segments"""
```

**Implementation Strategy**:
- Validate that at least 1 segment remains after edits
- Recalculate coverage and confidence after each edit
- Track all user edits in user_edits JSON field
- Prevent deletion of high-importance segments without explicit confirmation

### 4. API Routes (`src/server/api/projects.py` - extend)

```python
@router.post("/projects/{project_id}/story/parse")
async def parse_story(project_id: str):
    """Parse travel narrative into story segments"""
    # 1. Get project config
    # 2. Call StoryParser.parse_story()
    # 3. Update project status to "story_parsed"
    # 4. Return StorySkeleton

@router.get("/projects/{project_id}/skeleton/{skeleton_id}")
async def get_skeleton(project_id: str, skeleton_id: str):
    """Retrieve story skeleton"""
    # 1. Query skeleton from DB
    # 2. Query segments from DB
    # 3. Return StorySkeleton

@router.post("/projects/{project_id}/skeleton/{skeleton_id}/confirm")
async def confirm_skeleton(project_id: str, skeleton_id: str, request: SkeletonConfirmationRequest):
    """Confirm skeleton with user edits"""
    # 1. Call SkeletonConfirmation.confirm_skeleton()
    # 2. Update project status to "skeleton_confirmed"
    # 3. Return confirmed StorySkeleton

@router.get("/projects/{project_id}/skeleton/current")
async def get_current_skeleton(project_id: str):
    """Get latest confirmed skeleton"""
    # 1. Query latest confirmed skeleton
    # 2. Return StorySkeleton
```

### 5. Database Schema Updates (`src/server/storage/schemas.py`)

Add SQLAlchemy ORM models:
- `StorySegmentRecord`
- `StorySkeletonRecord`
- `SkeletonConfirmationRecord`

Update `Database` class to create new tables on initialization.

### 6. Tests

**Unit Tests** (`tests/unit/test_story_parser.py`):
- `test_parse_story_valid_narrative()` - Parse normal narrative
- `test_parse_story_short_narrative()` - Fallback for short narrative
- `test_parse_story_unstructured()` - Fallback for unstructured narrative
- `test_extract_entities()` - Entity extraction
- `test_cluster_segments()` - Segment clustering

**Unit Tests** (`tests/unit/test_skeleton_confirmation.py`):
- `test_confirm_skeleton_no_edits()` - Confirm without changes
- `test_confirm_skeleton_merge()` - Merge segments
- `test_confirm_skeleton_delete()` - Delete segment
- `test_confirm_skeleton_reorder()` - Reorder segments
- `test_confirm_skeleton_invalid_edits()` - Reject invalid edits

**Integration Tests** (`tests/integration/test_phase2_flow.py`):
- `test_complete_phase2_flow()` - Parse → Generate → Confirm
- `test_phase2_flow_with_edits()` - Parse → Generate → Confirm with user edits
- `test_phase2_flow_short_narrative()` - Fallback handling

---

## Files to Create/Modify

### New Files
- `src/shared/types.py` - Add StorySegment, StorySkeleton, SkeletonConfirmationRequest models
- `src/server/models/story.py` - Add story-related Pydantic models
- `src/server/modules/story_parser.py` - StoryParser implementation
- `src/server/modules/story_skeleton.py` - StorySkeleton implementation
- `src/server/modules/skeleton_confirmation.py` - SkeletonConfirmation implementation
- `tests/unit/test_story_parser.py` - Unit tests for StoryParser
- `tests/unit/test_skeleton_confirmation.py` - Unit tests for SkeletonConfirmation
- `tests/integration/test_phase2_flow.py` - Integration tests

### Modified Files
- `src/shared/types.py` - Add ProjectStatus enum values
- `src/server/storage/schemas.py` - Add ORM models for story tables
- `src/server/storage/database.py` - Update table creation logic
- `src/server/api/projects.py` - Add Phase 2 endpoints
- `src/server/main.py` - No changes needed (router already included)
- `requirements.txt` - Add NLP dependencies if needed (e.g., nltk, spacy)

---

## Implementation Sequence

1. **Data Models** - Define Pydantic models in `src/shared/types.py` and `src/server/models/story.py`
2. **Database Schema** - Add ORM models and update database initialization
3. **StoryParser Module** - Implement parsing logic with fallbacks
4. **StorySkeleton Module** - Implement skeleton generation
5. **SkeletonConfirmation Module** - Implement confirmation and edit logic
6. **API Routes** - Add Phase 2 endpoints
7. **Unit Tests** - Test each module independently
8. **Integration Tests** - Test complete Phase 2 workflow
9. **Documentation** - Update README with Phase 2 usage examples

---

## Verification & Testing

### Manual Testing
1. Create a project with a travel narrative
2. Call `POST /api/projects/{project_id}/story/parse` → Verify skeleton is generated
3. Call `GET /api/projects/{project_id}/skeleton/{skeleton_id}` → Verify segments are returned
4. Call `POST /api/projects/{project_id}/skeleton/{skeleton_id}/confirm` with edits → Verify edits are applied
5. Call `GET /api/projects/{project_id}/skeleton/current` → Verify confirmed skeleton is returned

### Automated Testing
- Run `pytest tests/unit/test_story_parser.py -v`
- Run `pytest tests/unit/test_skeleton_confirmation.py -v`
- Run `pytest tests/integration/test_phase2_flow.py -v`
- Verify all tests pass and coverage > 80%

### Integration with Phase 1
- Verify Phase 1 tests still pass
- Verify project status transitions correctly (ready → story_parsed → skeleton_confirmed)
- Verify database schema is backward compatible

---

## Key Design Decisions

1. **Simple parsing for MVP**: Use heuristics (sentence splitting, keyword extraction) rather than complex NLP. Can upgrade to LLM-based parsing later.

2. **Segment count constraint**: Enforce 3-8 segments to keep narrative manageable and ensure sufficient media alignment opportunities.

3. **Confidence scoring**: Track parsing confidence for each segment to inform downstream alignment decisions.

4. **User edit tracking**: Record all user modifications in user_edits JSON field for diagnostics and potential rollback.

5. **Status progression**: Extend ProjectStatus enum to track story parsing and skeleton confirmation stages.

6. **Fallback strategies**: Provide simplified parsing for short/unstructured narratives to ensure system doesn't fail.

---

## User Decisions (Confirmed)

1. **Story Parsing Strategy**: Use Kimi LLM for intelligent narrative parsing
   - Kimi will parse travel narrative into story segments with high quality
   - Requires Kimi API key in `.env`
   - Fallback: If Kimi unavailable, use simple heuristic-based parsing
   - Implementation: Add `kimi_api_key` to environment variables

2. **Segment Count**: 3-8 segments (fixed range)
   - Enforced in validation logic
   - Kimi will be instructed to generate 3-8 segments

3. **Confidence Threshold**: Always allow confirmation (user decides)
   - Generate skeleton regardless of confidence score
   - Display confidence to user for transparency
   - User can edit/confirm or request re-parsing
