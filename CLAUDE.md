# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Vlog Editor Fast** is an AI travel vlog editing system that transforms travel stories into 2-4 minute vlogs. The project is a Python FastAPI backend with a modular architecture supporting multiple processing phases: input validation, story parsing, media analysis, alignment, editing, and rendering.

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run unit tests only
python3 -m pytest tests/unit/ -v

# Run integration tests only
python3 -m pytest tests/integration/ -v

# Run specific test file
python3 -m pytest tests/unit/test_project_manager.py -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=html

# Run specific test by name
python3 -m pytest tests/unit/test_project_manager.py::TestProjectManager::test_create_project -v
```

### Code Quality
```bash
# Format code with Black (100 char line length)
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Check for linting issues without fixing
ruff check src/ tests/ --no-fix
```

### Running the Server
```bash
# Start FastAPI development server
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000

# API documentation available at http://localhost:8000/docs
```

## Architecture Overview

### Directory Structure
```
src/
├── server/                    # Backend service
│   ├── main.py               # FastAPI app initialization
│   ├── api/                  # API route handlers
│   ├── models/               # Pydantic data models
│   ├── storage/              # Database layer (SQLAlchemy)
│   └── modules/              # Core processing modules
├── shared/                   # Shared types and contracts
└── client/                   # Frontend (not implemented)

tests/
├── unit/                     # Unit tests for individual modules
└── integration/              # End-to-end workflow tests
```

### Core Modules (src/server/modules/)

The system is organized as a pipeline of processing stages:

1. **ProjectManager** (`project_manager.py`) - Creates projects and manages workspace initialization
2. **InputValidator** (`input_validator.py`) - Validates input contracts and generates validation reports
3. **AssetIndexer** (`asset_indexer.py`) - Indexes media files and extracts metadata
4. **StoryParser** (`story_parser.py`) - Parses travel narrative into story segments (uses Kimi LLM with heuristic fallback)
5. **MediaAnalyzer** (`media_analyzer.py`) - Analyzes media assets for visual/audio characteristics
6. **AlignmentEngine** (`alignment_engine.py`) - Aligns story segments with media assets
7. **HighlightConfirmation** (`highlight_confirmation.py`) - Identifies and confirms highlight moments
8. **EditPlanner** (`edit_planner.py`) - Plans edit sequences and transitions
9. **NarrationEngine** (`narration_engine.py`) - Generates narration from story segments
10. **AudioComposer** (`audio_composer.py`) - Composes audio tracks (narration + BGM)
11. **Renderer** (`renderer.py`) - Renders final video output
12. **RunOrchestrator** (`run_orchestrator.py`) - Orchestrates the complete pipeline
13. **StorySkeleton** (`story_skeleton.py`) - Manages story skeleton data structure
14. **SkeletonConfirmation** (`skeleton_confirmation.py`) - Handles user confirmation of story skeletons
15. **ArtifactStore** (`artifact_store.py`) - Manages intermediate artifacts and versioning
16. **DiagnosticReporter** (`diagnostic_reporter.py`) - Generates diagnostic reports

### Data Models (src/server/models/)

- **project.py** - ProjectConfig, ProjectMetadata
- **media.py** - Media file models
- **validation.py** - Validation report models

### Database Layer (src/server/storage/)

- **database.py** - SQLite connection management, project-specific DB paths
- **schemas.py** - SQLAlchemy ORM models
- Project databases stored at: `~/.vlog-editor/projects/{project_id}/project.db`

### API Routes (src/server/api/)

- `POST /api/projects/create` - Create new project
- `GET /api/projects/{project_id}` - Get project info
- `POST /api/projects/{project_id}/validate` - Validate input
- `GET /api/projects/{project_id}/assets` - Get asset index
- `GET /health` - Health check

## Key Design Patterns

### Module Pattern
Each module follows a consistent pattern:
- Static methods for main operations
- Validation before processing
- Database persistence of results
- Error handling with fallbacks (e.g., StoryParser uses Kimi LLM with heuristic fallback)

### Data Flow
1. Input validation → 2. Asset indexing → 3. Story parsing → 4. Media analysis → 5. Alignment → 6. Highlight confirmation → 7. Edit planning → 8. Narration → 9. Audio composition → 10. Rendering

### Database Strategy
- SQLite for local storage
- Project-isolated databases (one DB per project)
- SQLAlchemy ORM for schema management
- Schemas defined in `storage/schemas.py`

## Code Style & Conventions

- **Formatting**: Black with 100 character line length
- **Linting**: Ruff
- **Python Version**: 3.10+
- **Type Hints**: Use Pydantic models for API contracts
- **Async**: FastAPI uses async/await; pytest-asyncio handles async tests
- **Comments**: Minimal; use docstrings for module/class/function documentation

## Testing Strategy

- **Unit Tests**: Test individual modules in isolation
- **Integration Tests**: Test end-to-end workflows
- **Test Files**: Located in `tests/unit/` and `tests/integration/` with `test_` prefix
- **Fixtures**: Use pytest fixtures for common setup (database, mock data)
- **Async Tests**: Use `pytest-asyncio` for async test functions

## Dependencies

Key dependencies:
- **FastAPI** (0.104.1) - Web framework
- **SQLAlchemy** (2.0.23) - ORM
- **Pydantic** (2.5.0) - Data validation
- **OpenCV** (4.8.1.78) - Video/image processing
- **Librosa** (0.10.0) - Audio processing
- **Pillow** (10.1.0) - Image manipulation
- **Pytest** (7.4.3) - Testing framework

## Environment Variables

See `.env.example` for configuration:
- `KIMI_API_KEY` - API key for Kimi LLM (optional; story parser falls back to heuristics)
- Database paths are auto-generated per project

## Common Tasks

### Adding a New Module
1. Create file in `src/server/modules/`
2. Follow existing module pattern (static methods, validation, DB persistence)
3. Add corresponding tests in `tests/unit/test_<module_name>.py`
4. Update `RunOrchestrator` if part of main pipeline

### Adding a New API Endpoint
1. Create route handler in `src/server/api/`
2. Use Pydantic models for request/response validation
3. Add integration tests in `tests/integration/`

### Debugging
- Use `print()` or logging for quick debugging
- Run single test with `-v` flag for detailed output
- Check database at `~/.vlog-editor/projects/{project_id}/project.db` for persisted state

## Recent Changes

The project has completed Phases 1-6:
- Phase 1: Infrastructure & Input Processing
- Phase 2: Story Parsing & Skeleton Management
- Phase 3: Media Analysis & Alignment
- Phase 4: Final Composition & Export
- Phase 5: Version Management & Recovery
- Phase 6: Testing & Optimization

See git history and `docs/` directory for detailed phase documentation.

## Notes for Future Work

- Client frontend not yet implemented
- Kimi LLM integration is optional with heuristic fallback
- Performance profiling results available in `performance_results/` directory
- Comprehensive test documentation in `docs/testing/`
