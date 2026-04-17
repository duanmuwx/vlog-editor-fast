# Phase 4 Implementation Plan: Final Composition & Export

## Context

Phases 1-3 established infrastructure, story parsing, media analysis, and highlight confirmation. Phase 4 completes the pipeline by transforming confirmed highlights into a finished 2-4 minute vlog with narration, audio mixing, and video rendering.

**Goal**: Implement 7 new modules (EditPlanner, NarrationEngine, AudioComposer, Renderer, RunOrchestrator, ArtifactStore, DiagnosticReporter) to generate executable timelines, produce voiceovers with subtitles, mix audio tracks, render final video, and support local regeneration (narration-only, audio-only, shorter-cut).

**Why this matters**: Phase 4 is the final step that transforms story structure and media selections into a shareable vlog. It must handle graceful degradation, preserve user decisions across regenerations, and support local re-editing without re-importing media. Success metrics: 2-4 minute output, ≥80% success rate, ≤120 minutes total processing time, ≤3 user interventions.

---

## Architecture Overview

### New Modules (7 total)

1. **EditPlanner** - Generates executable timeline from story and highlights
   - Input: confirmed story skeleton, confirmed highlight selections
   - Output: Timeline with clips, transitions, timing, and pacing
   - Responsibility: Arrange clips chronologically, apply transitions, calculate durations, support compression to target length

2. **NarrationEngine** - Generates voiceover, subtitles, and text cards
   - Input: story skeleton, timeline, TTS voice preference
   - Output: Narration pack with TTS audio, SRT subtitles, text cards
   - Responsibility: Generate narration text, call TTS API, create subtitles, generate text cards for transitions

3. **AudioComposer** - Mixes narration, ambient sound, and BGM
   - Input: timeline, narration pack, BGM asset, ambient sound tracks
   - Output: Mixed audio pack with balanced tracks
   - Responsibility: Volume normalization, track mixing, preserve ambient sound moments, BGM integration

4. **Renderer** - Renders final video with subtitles and exports
   - Input: timeline, audio mix pack, subtitles, visual assets
   - Output: MP4 video, SRT subtitles, narration MP3, manifest JSON
   - Responsibility: Video composition, subtitle rendering, format conversion, export

5. **RunOrchestrator** - Manages project state machine and task scheduling
   - Input: Project state, task dependencies
   - Output: Updated project status, task execution results
   - Responsibility: State transitions, task scheduling, failure recovery, local regeneration support

6. **ArtifactStore** - Manages version lifecycle and dependencies
   - Input: Artifact metadata, upstream versions
   - Output: Version records with dependency tracking
   - Responsibility: Version creation, invalidation, rollback, dependency management

7. **DiagnosticReporter** - Aggregates diagnostics and fallback events
   - Input: Events from all modules
   - Output: Diagnostic bundle with run summary
   - Responsibility: Collect diagnostics, track fallback reasons, generate user-facing messages

### Data Models (New)

**Timeline** (Pydantic model in `src/shared/types.py`):
```python
class TimelineClip(BaseModel):
    clip_id: str  # UUID
    shot_id: str  # Reference to MediaShot
    start_time: float  # Seconds in timeline
    end_time: float  # Seconds in timeline
    transition: str  # "cut", "fade", "dissolve"
    duration: float  # Calculated as end_time - start_time

class TimelineSegment(BaseModel):
    segment_id: str  # Reference to StorySegment
    clips: List[TimelineClip]  # Clips for this segment
    narration_start: float  # When narration starts
    narration_end: float  # When narration ends
    total_duration: float  # Total segment duration

class Timeline(BaseModel):
    timeline_id: str  # UUID
    project_id: str  # FK to projects
    version_id: str  # Version identifier
    segments: List[TimelineSegment]  # Ordered segments
    total_duration_seconds: float  # Total video duration
    target_duration_seconds: float  # Target duration (2-4 min)
    created_at: datetime
```

**NarrationPack** (Pydantic model):
```python
class Subtitle(BaseModel):
    subtitle_id: str  # UUID
    text: str  # Subtitle text
    start_time: float  # Seconds
    end_time: float  # Seconds

class TextCard(BaseModel):
    card_id: str  # UUID
    text: str  # Card text
    duration_seconds: float  # Display duration
    position: str  # "center", "top", "bottom"

class NarrationPack(BaseModel):
    narration_id: str  # UUID
    project_id: str  # FK to projects
    version_id: str  # Version identifier
    narration_text: str  # Full narration text
    tts_audio_path: str  # Path to TTS audio file
    subtitles: List[Subtitle]  # Subtitle entries
    text_cards: List[TextCard]  # Text cards for transitions
    tts_voice: str  # Voice used for TTS
    created_at: datetime
```

**AudioMixPack** (Pydantic model):
```python
class AudioTrack(BaseModel):
    track_id: str  # UUID
    track_type: str  # "narration", "ambient", "bgm"
    file_path: str  # Path to audio file
    volume: float  # Volume level (0.0-1.0)
    start_time: float  # When track starts
    end_time: float  # When track ends

class AudioMixPack(BaseModel):
    audio_mix_id: str  # UUID
    project_id: str  # FK to projects
    version_id: str  # Version identifier
    tracks: List[AudioTrack]  # All audio tracks
    mixed_audio_path: str  # Path to final mixed audio
    total_duration_seconds: float  # Duration of mixed audio
    created_at: datetime
```

**ExportBundle** (Pydantic model):
```python
class ExportBundle(BaseModel):
    export_id: str  # UUID
    project_id: str  # FK to projects
    version_id: str  # Version identifier
    video_path: str  # Path to MP4 file
    subtitle_path: str  # Path to SRT file
    narration_path: str  # Path to narration MP3
    manifest_path: str  # Path to manifest JSON
    status: str  # "success", "partial", "failed"
    created_at: datetime
```

**ArtifactVersion** (Pydantic model):
```python
class ArtifactVersion(BaseModel):
    version_id: str  # UUID
    artifact_type: str  # "timeline", "narration", "audio_mix", "export"
    project_id: str  # FK to projects
    upstream_versions: Dict[str, str]  # Dependencies: {"timeline_id": "v1", ...}
    status: str  # "active", "superseded", "invalidated"
    created_at: datetime
    invalidated_at: Optional[datetime]
```

### Database Schema (New Tables)

16 new tables for Phase 4:
- `edit_plans`, `timelines`, `timeline_segments`, `timeline_clips`
- `narrations`, `subtitles`, `text_cards`
- `audio_mixes`, `audio_tracks`
- `exports`, `export_logs`
- `artifact_versions`, `run_records`, `task_states`
- `diagnostics`, `fallback_events`

### API Endpoints (New)

```
POST /api/projects/{project_id}/edit-plan
POST /api/projects/{project_id}/generate-narration
POST /api/projects/{project_id}/mix-audio
POST /api/projects/{project_id}/render-export
POST /api/projects/{project_id}/regenerate/{type}
GET /api/projects/{project_id}/timeline/{version_id}
GET /api/projects/{project_id}/narration/{version_id}
GET /api/projects/{project_id}/audio-mix/{version_id}
GET /api/projects/{project_id}/exports
GET /api/projects/{project_id}/diagnostics/{run_id}
```

### Project Status Extension

Add to `ProjectStatus` enum:
- `EDIT_PLANNED`
- `NARRATION_GENERATED`
- `AUDIO_MIXED`
- `EXPORTED`

---

## Implementation Details

### 1. EditPlanner Module (`src/server/modules/edit_planner.py`)

**Responsibility**: Generate executable timeline from confirmed story and highlights

**Key Methods**:
- `plan_edit(project_id)` - Generate timeline from story and highlights
- `_arrange_clips(segment, selections)` - Arrange clips with transitions
- `_calculate_durations(clips)` - Calculate total duration
- `_compress_to_duration(timeline, target_seconds)` - Compress to target duration

**Implementation Strategy**:
- Arrange clips chronologically by shot start time
- Use "cut" transitions by default, "fade" for segment boundaries
- If total > 4 minutes, compress by removing low-importance clips
- Preserve user's "must keep" and "memorial" selections
- Validate all high-importance segments have ≥1 clip or alternative render unit

### 2. NarrationEngine Module (`src/server/modules/narration_engine.py`)

**Responsibility**: Generate voiceover, subtitles, and text cards

**Key Methods**:
- `generate_narration(project_id, timeline_id, tts_voice)` - Generate narration pack
- `_generate_narration_text(segments)` - Generate narration text
- `_call_tts_api(text, voice)` - Call TTS API
- `_generate_subtitles(text, audio_duration)` - Generate subtitles
- `_generate_text_cards(segments)` - Generate text cards

**Implementation Strategy**:
- Generate narration by concatenating segment summaries
- Call TTS API (Azure TTS, Google TTS, etc.) with specified voice
- Fallback: If TTS unavailable, use silence or pre-recorded audio
- Generate subtitles by splitting narration into 5-10 second chunks
- Generate text cards for segment transitions
- Validate narration ≤ 20 seconds per segment

### 3. AudioComposer Module (`src/server/modules/audio_composer.py`)

**Responsibility**: Mix narration, ambient sound, and BGM

**Key Methods**:
- `compose_audio(project_id, timeline_id, narration_id, bgm_asset)` - Mix audio
- `_extract_ambient_sound(timeline)` - Extract ambient sound from clips
- `_normalize_levels(tracks)` - Normalize audio levels
- `_mix_tracks(tracks)` - Mix audio tracks using FFmpeg

**Implementation Strategy**:
- Extract ambient sound from original video clips (preserve ≥3 moments)
- Normalize narration to -20dB, ambient to -30dB, BGM to -25dB
- Use FFmpeg for audio mixing
- Fallback: If ambient unavailable, use BGM only
- Validate final audio duration matches video duration

### 4. Renderer Module (`src/server/modules/renderer.py`)

**Responsibility**: Render final video with subtitles and export

**Key Methods**:
- `render_export(project_id, timeline_id, audio_mix_id, narration_id)` - Render and export
- `_compose_video(timeline)` - Compose video from clips
- `_render_subtitles(subtitles, video_path)` - Render subtitles onto video
- `_mux_audio_video(video_path, audio_path)` - Mux audio and video
- `_export_srt(subtitles)` - Export SRT subtitles
- `_generate_manifest(timeline, export_bundle)` - Generate manifest JSON

**Implementation Strategy**:
- Use FFmpeg for video composition and muxing
- Render subtitles using FFmpeg subtitle filter
- Export MP4 with H.264 codec, 1920x1080 resolution, 16:9 aspect ratio
- Export SRT subtitles in standard format
- Export narration as MP3 for user reference
- Generate manifest JSON with metadata
- Fallback: If rendering fails, preserve intermediate products for re-export

### 5. RunOrchestrator Module (`src/server/modules/run_orchestrator.py`)

**Responsibility**: Manage project state machine and task scheduling

**Key Methods**:
- `run_phase4(project_id)` - Execute full Phase 4 pipeline
- `regenerate_narration(project_id)` - Regenerate narration only
- `regenerate_audio(project_id)` - Regenerate audio only
- `regenerate_shorter(project_id, target_seconds)` - Regenerate with shorter duration
- `_handle_failure(project_id, run_id, error)` - Handle failure

**Implementation Strategy**:
- Create run record at start, update status as each stage completes
- Support recovery from failures at module level
- Preserve intermediate products for re-export
- Track task states for each stage
- Support local regeneration by reusing upstream artifacts

### 6. ArtifactStore Module (`src/server/modules/artifact_store.py`)

**Responsibility**: Manage version lifecycle and dependencies

**Key Methods**:
- `create_version(artifact_type, project_id, upstream_versions)` - Create version
- `get_version(version_id)` - Retrieve version
- `invalidate_version(version_id)` - Invalidate version and downstream
- `get_active_version(project_id, artifact_type)` - Get active version
- `rollback_version(project_id, artifact_type, version_id)` - Rollback version

**Implementation Strategy**:
- Track upstream dependencies for each version
- Invalidate downstream versions when upstream changes
- Support version rollback for local regeneration
- Maintain version history for diagnostics

### 7. DiagnosticReporter Module (`src/server/modules/diagnostic_reporter.py`)

**Responsibility**: Aggregate diagnostics and fallback events

**Key Methods**:
- `report_diagnostics(project_id, run_id)` - Aggregate diagnostics
- `log_diagnostic(project_id, run_id, issue_type, severity, message)` - Log diagnostic
- `log_fallback(project_id, run_id, reason, action, details)` - Log fallback
- `generate_summary(diagnostics, fallbacks)` - Generate run summary

**Implementation Strategy**:
- Collect diagnostics from all modules during execution
- Track fallback reasons and actions
- Generate user-facing messages for failures
- Support debugging and troubleshooting

---

## Files to Create/Modify

### New Files
- `src/server/modules/edit_planner.py`
- `src/server/modules/narration_engine.py`
- `src/server/modules/audio_composer.py`
- `src/server/modules/renderer.py`
- `src/server/modules/run_orchestrator.py`
- `src/server/modules/artifact_store.py`
- `src/server/modules/diagnostic_reporter.py`
- `tests/unit/test_edit_planner.py`
- `tests/unit/test_narration_engine.py`
- `tests/unit/test_audio_composer.py`
- `tests/unit/test_renderer.py`
- `tests/unit/test_artifact_store.py`
- `tests/integration/test_phase4_flow.py`

### Modified Files
- `src/shared/types.py` - Add Phase 4 data models and ProjectStatus values
- `src/server/storage/schemas.py` - Add ORM models for Phase 4 tables
- `src/server/storage/database.py` - Update table creation logic
- `src/server/api/projects.py` - Add Phase 4 endpoints
- `requirements.txt` - Add FFmpeg Python bindings if needed

---

## Implementation Sequence

1. Data Models - Add Phase 4 models to `src/shared/types.py`
2. Database Schema - Add ORM models to `src/server/storage/schemas.py`
3. ArtifactStore - Implement version management (foundation)
4. RunOrchestrator - Implement task orchestration
5. EditPlanner - Implement timeline generation
6. NarrationEngine - Implement TTS and subtitles
7. AudioComposer - Implement audio mixing
8. Renderer - Implement video rendering
9. DiagnosticReporter - Implement diagnostics
10. API Routes - Add Phase 4 endpoints
11. Unit Tests - Test each module
12. Integration Tests - Test complete workflow
13. Documentation - Update README

---

## Verification & Testing

### Manual Testing
1. Create project with narrative and media
2. Parse story, confirm skeleton, analyze media, align, confirm highlights
3. Call `POST /api/projects/{project_id}/edit-plan` → Verify timeline
4. Call `POST /api/projects/{project_id}/generate-narration` → Verify narration
5. Call `POST /api/projects/{project_id}/mix-audio` → Verify audio mix
6. Call `POST /api/projects/{project_id}/render-export` → Verify MP4 export
7. Call `POST /api/projects/{project_id}/regenerate/narration` → Verify narration-only
8. Call `POST /api/projects/{project_id}/regenerate/audio` → Verify audio-only
9. Call `POST /api/projects/{project_id}/regenerate/shorter` → Verify shorter-cut

### Automated Testing
- Run all unit tests for Phase 4 modules
- Run integration tests for complete workflow
- Verify coverage > 80%
- Verify Phases 1-3 tests still pass

### Performance Testing
- Measure total processing time (target: ≤120 minutes)
- Measure local regeneration time (target: ≤30 min for narration/audio, ≤60 min for shorter)
- Verify memory usage within bounds

---

## Key Design Decisions

1. **Version-based artifact management** - Each artifact has version_id with upstream dependency tracking for local regeneration
2. **Graceful degradation** - Fallback strategies for missing TTS, ambient sound, rendering failures
3. **User decision preservation** - Track "must keep" and "memorial" selections across regenerations
4. **Module-level recovery** - Failure recovery at module level, not full project re-run
5. **Diagnostic aggregation** - Unified DiagnosticBundle with fallback tracking
6. **Timeline compression** - Support compression to target duration while preserving high-importance segments
7. **Subtitle generation** - Auto-generate from narration with timing alignment
8. **Audio mixing** - Preserve ≥3 ambient sound moments with proper level balancing

---

## Success Metrics (From PRD)

- **North Star**: Generate 2-4 minute, 16:9 vlogs with user satisfaction ≥4/5
- **Experience**: ≤120 minutes total processing, ≤3 user interventions, ≥1 local regeneration
- **Quality**: Every high-importance segment has ≥1 usable shot or alternative render unit, ≤15% duplicate shots, ≤20 seconds continuous narration, ≥3 ambient sound moments
- **Performance**: Must run on CPU devices, module-level retry support, reuse intermediate results
- **Stability**: ≥80% end-to-end success rate, all failures locatable to specific module, preserve intermediate products on export failure

---

## User Decisions (To Be Confirmed)

1. **TTS Service** - Which TTS service? (Azure TTS recommended)
2. **Video Codec** - H.264 at 1920x1080 (16:9)?
3. **Subtitle Rendering** - Burn into video and export SRT?
4. **Ambient Sound Preservation** - How many moments? (3-5 recommended)
5. **Local Regeneration Scope** - Support all three types (narration, audio, shorter)?
