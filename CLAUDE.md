# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI travel vlog editing system—a local tool that transforms travel stories into 2–4 minute, 16:9 horizontal-format vlogs. **Phases 1–5 are fully implemented** with core modules, API, database, and test suite (21 tests, all passing).

**Core principle:** Story-first, multi-modal alignment. The user's travel narrative (游记) is the primary driver; photos, videos, audio, timestamps, and GPS data are evidence that supports the story structure.

**Current Phase:** Phase 1–5 complete. Phase 6 (UI/Frontend) and Phase 7 (Optimization) pending.

## Architecture & Core Concepts

### System Flow

1. **Input**: User provides a travel narrative (text), media files (photos/videos), and optional metadata (EXIF, GPS, timestamps)
2. **Story Analysis**: LLM parses the narrative into a story structure (scenes, key moments, emotional beats)
3. **Media Alignment**: Multi-modal matching aligns narrative segments with photos/videos using time, location, visual content, and audio cues
4. **Highlight Selection**: System identifies candidate "highlight" clips; user confirms or adjusts (single human checkpoint)
5. **Composition**: Auto-generate structure, transitions, pacing, and timing
6. **Audio**: Generate AI voiceover (TTS), preserve ambient sound, mix background music
7. **Rendering**: Export MP4, subtitles, voiceover track, and edit manifest

### Key Design Principles

- **Story-first**: Narrative structure drives editing decisions, not media quality alone
- **High-confidence automation**: Deduplication, sorting, waste removal, candidate selection, subtitle generation are fully automatic
- **Single user checkpoint**: Only highlight confirmation requires human input; everything else is automatic
- **Multi-modal alignment**: Leverage text, visuals, audio, time, and location simultaneously
- **Graceful degradation**: When metadata is missing (no EXIF, no GPS, no speech), fall back to content-based matching and confidence scoring

### Core Modules (Conceptual)

| Module | Responsibility |
|--------|---|
| **Project Manager** | Orchestrates the pipeline, manages task state and recovery |
| **Story Parser** | Parses narrative into scenes, segments, and emotional beats |
| **Media Analyzer** | Extracts visual features, speech, metadata from photos/videos |
| **Alignment Engine** | Matches narrative segments to media using multi-modal signals |
| **EditPlan Generator** | Produces structure, timing, transitions, and pacing decisions |
| **Composer** | Assembles final video: cuts, transitions, effects, timing |
| **Audio Mixer** | Generates voiceover, mixes ambient sound and BGM |
| **Renderer** | Exports MP4, subtitles, voiceover, and manifest |

## Critical Constraints & Open Questions

### P0 Issues (Must Resolve Before MVP)

1. **Quantified success metrics**: Define acceptable thresholds for processing time, success rate, manual correction rate, user satisfaction
2. **User correction entry points**: Current design has only one checkpoint (highlight confirmation); need "three-stage light interaction" (story skeleton → highlights → local regeneration)
3. **Alignment strategy vs. real-world data**: Metadata is often missing; need explicit fallback strategies for no-EXIF, no-GPS, no-speech, short-narrative cases
4. **Local-first boundary**: Clarify which operations must run locally vs. which can be cloud-optional; define minimum/recommended hardware specs
5. **Confidence & fallback strategy**: Define how to handle low-confidence matches and when to degrade gracefully

### P1 Issues (Should Resolve for MVP)

- Long-task state management and recovery (checkpoint/resume design)
- Tension between "story-first" and "remove low-quality media" (preserve sentimental value)
- Local re-generation capability (e.g., rewrite voiceover only, remix audio only, restructure only)
- Input validation and quality requirements (media count, duration, narrative length, file formats)

### P2 Issues (Post-MVP)

- Diagnostic output and logging for debugging
- Version boundaries and decision principles (what V1 does vs. doesn't do)

## Document Map

### Product Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [PRD](docs/product/PRD.md) | Primary PRD; product requirements, success metrics, version boundaries | Product, engineering, design |
| [Architecture](docs/product/architecture.md) | Solution architecture and design principles | Engineering, design |
| [Tools Research](docs/product/tools_research.md) | Dependency evaluation and tool research | Engineering |
| [Data Schema](docs/product/data_schema.md) | Data dictionary and schema definitions | Engineering |
| [Interaction Design](docs/product/interaction_design.md) | UI/UX design and interaction flows | Design, product |
| [Test Cases](docs/product/test_cases.md) | Acceptance test cases and scenarios | QA, product |

### Implementation Plans

| Phase | Plan Document | Scope |
|-------|---------------|-------|
| **Overview** | [Implementation Phases Overview](plans/implementation-phases-overview.md) | Complete system design, all 5 phases, data models, API design, validation criteria |
| **Phase 1** | [Phase 1: Infrastructure & Input Processing](plans/phase1-implementation.md) | Project management, input validation, media asset indexing |
| **Phase 2** | [Phase 2: Story Analysis & Confirmation](plans/phase2-story-analysis-confirmation.md) | Story parsing, skeleton generation, user confirmation workflow |
| **Phase 3** | [Phase 3: Media Analysis & Alignment](plans/phase3-media-analysis-alignment.md) | Media analysis, narrative-media alignment, highlight confirmation |
| **Phase 4** | [Phase 4: Final Composition & Export](plans/phase4-final-composition-export.md) | Edit planning, narration/TTS, audio mixing, video rendering |
| **Phase 5** | [Phase 5: Version Management & Recovery](plans/phase5-version-management-recovery.md) | Run orchestration, artifact versioning, local regeneration, diagnostics |
| **Phase 6** | [Phase 6: Testing & Optimization](plans/phase6-testing-optimization.md) | Unit/integration/E2E testing, performance optimization, documentation |

### Repository Guidelines

| Document | Purpose | Audience |
|----------|---------|----------|
| `AGENTS.md` | Repository guidelines for documentation and commits | All contributors |

## Development Commands

### Setup & Installation

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_project_manager.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```

### Running the Server

```bash
# Start FastAPI development server (auto-reload)
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Implemented Modules

| Module | Status | Responsibility |
|--------|--------|---|
| **ProjectManager** | ✅ | Project creation, workspace management |
| **InputValidator** | ✅ | Input validation, risk identification |
| **AssetIndexer** | ✅ | Media indexing, metadata extraction |
| **StoryParser** | ✅ | Narrative parsing into scenes/segments |
| **StorySkeleton** | ✅ | Story structure representation |
| **SkeletonConfirmation** | ✅ | User confirmation UI logic |
| **MediaAnalyzer** | ✅ | Visual/audio feature extraction |
| **AlignmentEngine** | ✅ | Multi-modal narrative-media matching |
| **EditPlanner** | ✅ | Structure, timing, transitions generation |
| **HighlightConfirmation** | ✅ | Highlight selection confirmation |
| **Composer** | ✅ | Video assembly and effects |
| **AudioComposer** | ✅ | Voiceover, ambient sound, BGM mixing |
| **NarrationEngine** | ✅ | TTS voiceover generation |
| **Renderer** | ✅ | MP4 export, subtitle generation |
| **RunOrchestrator** | ✅ | Pipeline orchestration, state management |
| **ArtifactStore** | ✅ | Version management, recovery |
| **DiagnosticReporter** | ✅ | Logging, diagnostics, debugging |

## Database

SQLite database per project at: `~/.vlog-editor/projects/{project_id}/project.db`

Key tables: `projects`, `project_configs`, `media_files`, `validation_reports`, `asset_indexes`, `story_skeletons`, `edit_plans`, `artifacts`

## Three-Stage User Interaction Model

1. **Story Skeleton Confirmation** - User reviews and adjusts parsed narrative structure
2. **Highlight Confirmation** - User confirms/adjusts candidate highlight clips
3. **Local Regeneration** - User can regenerate specific components (voiceover, audio mix, structure) without full re-processing

## Quick Reference

### When Adding or Modifying Content

- **Terminology**: Use established names (`Project Manager`, `Media Analyzer`, `EditPlan`, `Story Parser`, etc.) consistently across all documents
- **Cross-references**: Update links when module names or flow steps change
- **Scope clarity**: Always mark whether a feature is V1, V2, or post-MVP
- **Fallback strategies**: When describing a core algorithm, include the degradation path for missing data

### Before Opening a PR

- Run `git diff --check` to catch trailing whitespace
- Search for unresolved placeholders: `rg -n "TODO|待确认|TBD" *.md`
- Verify document structure: `sed -n '1,80p' AI旅行Vlog剪辑系统PRD重构版.md`
- Preview Markdown in your editor to check tables, lists, and heading hierarchy

### Planning & Implementation

- Use `/init` to scaffold a new CLAUDE.md or update this one
- Use plan mode (`EnterPlanMode`) for multi-step implementation tasks
- Save plans to `plans/` directory via the PostToolUse hook in `.claude/settings.json`
- Keep implementation plans focused on the specific task; avoid over-designing for hypothetical future requirements

## Key Decisions & Rationale

- **Documentation-first approach**: The system is complex and multi-disciplinary; written specifications prevent misalignment before code is written
- **Single checkpoint design**: Reduces user friction; high-confidence automation handles the rest
- **Story-driven architecture**: Distinguishes this from generic video editors; narrative structure is the organizing principle
- **Local-first with optional cloud**: Respects user privacy and offline use; cloud services are optional enhancements, not required

## Implementation Status

**Completed (Phases 1–5):**
- ✅ Infrastructure & input processing (Phase 1)
- ✅ Story analysis & confirmation (Phase 2)
- ✅ Media analysis & alignment (Phase 3)
- ✅ Final composition & export (Phase 4)
- ✅ Version management & recovery (Phase 5)

**Next Steps (Phases 6–7):**
1. Frontend UI implementation (Phase 6) - Web interface for three-stage interaction
2. Performance optimization & profiling (Phase 7)
3. Real-world testing with travel media samples
4. User feedback integration and iteration
5. Documentation and deployment guides

## Development Workflow

1. **Before starting work**: Check `plans/` directory for existing implementation plans
2. **During implementation**: Use `EnterPlanMode` for multi-step tasks; save plans to `plans/`
3. **Testing**: Run `pytest tests/ -v` before committing
4. **Code quality**: Run `black` and `ruff` before committing
5. **Committing**: Use descriptive messages; reference phase/module in commit
6. **Documentation**: Update relevant docs in `docs/product/` and `docs/developer_guide/`

## Key Files & Locations

| File/Directory | Purpose |
|---|---|
| `src/server/main.py` | FastAPI application entry point |
| `src/server/modules/` | Core module implementations |
| `src/server/storage/` | Database layer (SQLite) |
| `src/shared/types.py` | Shared type definitions |
| `tests/unit/` | Unit tests (18 tests) |
| `tests/integration/` | Integration tests (3 tests) |
| `docs/product/` | Product documentation (PRD, architecture, etc.) |
| `docs/testing/` | Test reports and verification |
| `plans/` | Implementation plans and design docs |
