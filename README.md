# Vlog Editor Fast - Phase 1 Implementation

AI travel vlog editing system - transforms travel stories into 2-4 minute vlogs.

## Phase 1: Infrastructure & Input Processing

This is the first phase of the project, focusing on:
- Project management and workspace creation
- Input validation and risk identification
- Media asset indexing and metadata extraction

## Project Structure

```
src/
├── server/                 # Python backend service
│   ├── main.py            # FastAPI application
│   ├── models/            # Data models
│   ├── modules/           # Core modules (ProjectManager, InputValidator, AssetIndexer)
│   ├── storage/           # Database layer
│   └── api/               # API routes
├── shared/                # Shared types
└── client/                # Frontend (not implemented yet)

tests/
├── unit/                  # Unit tests
└── integration/           # Integration tests
```

## Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run unit tests only
python3 -m pytest tests/unit/ -v

# Run integration tests only
python3 -m pytest tests/integration/ -v

# Run specific test file
python3 -m pytest tests/unit/test_project_manager.py -v
```

## Running the Server

```bash
# Start FastAPI server
uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /api/projects/create` - Create a new project
- `GET /api/projects/{project_id}` - Get project information
- `POST /api/projects/{project_id}/validate` - Validate project input
- `GET /api/projects/{project_id}/assets` - Get asset index
- `GET /health` - Health check

## Core Modules

### ProjectManager
Manages project creation and configuration.

```python
from src.server.modules.project_manager import ProjectManager
from src.shared.types import ProjectInputContract

# Create a project
input_contract = ProjectInputContract(
    project_name="My Travel Vlog",
    travel_note="Travel narrative text...",
    media_files=["/path/to/video.mp4", "/path/to/photo.jpg"],
    bgm_asset="bgm.mp3",
    tts_voice="female"
)

project_id = ProjectManager.create_project(input_contract)
```

### InputValidator
Validates project input and generates validation reports.

```python
from src.server.modules.input_validator import InputValidator

validation_report = InputValidator.validate(project_id, input_contract)
print(f"Valid: {validation_report.is_valid}")
print(f"Errors: {validation_report.errors}")
print(f"Warnings: {validation_report.warnings}")
```

### AssetIndexer
Indexes media assets and extracts metadata.

```python
from src.server.modules.asset_indexer import AssetIndexer

asset_index = AssetIndexer.index_assets(project_id, media_files)
print(f"Total videos: {asset_index.total_videos}")
print(f"Total photos: {asset_index.total_photos}")
print(f"Total duration: {asset_index.total_duration}s")
```

## Database

The system uses SQLite for local storage. Each project has its own database at:
```
~/.vlog-editor/projects/{project_id}/project.db
```

### Database Tables
- `projects` - Project metadata
- `project_configs` - Project configuration
- `media_files` - Indexed media files
- `validation_reports` - Validation results
- `asset_indexes` - Asset index records

## Validation Rules

| Check | Rule | Error/Warning |
|-------|------|---------------|
| Narrative length | ≥150 characters | Error if too short |
| Video count | ≥5 recommended | Warning if below |
| Photo count | ≥50 recommended | Warning if below |
| Total duration | ≥10 minutes | Error if too short |
| File format | Supported formats | Error if unsupported |
| File access | File exists and readable | Error if not |

## Test Coverage

- **Unit Tests**: 18 tests covering individual modules
- **Integration Tests**: 3 tests covering end-to-end flows
- **Total**: 21 tests, all passing

## Next Steps

Phase 2 will implement:
- Story Parser - Parse travel narrative into story segments
- Story Skeleton Confirmation UI - User confirmation interface
- Story skeleton versioning and management

## Configuration

See `.env.example` for environment variables:
```bash
cp .env.example .env
# Edit .env as needed
```

## Development

### Code Style
- Use Black for formatting
- Use Ruff for linting
- Follow PEP 8 conventions

### Adding Tests
Place new tests in `tests/unit/` or `tests/integration/` with `test_` prefix.

## License

MIT
