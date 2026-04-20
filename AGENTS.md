# Repository Guidelines

## Project Structure & Module Organization
Core application code lives in `src/`. The backend API is in `src/server`, with `api/` for FastAPI routes, `modules/` for pipeline stages such as parsing, alignment, narration, and rendering, `models/` for domain models, and `storage/` for SQLite persistence. Shared Pydantic types live in `src/shared`. Tests are organized by scope in `tests/unit`, `tests/integration`, `tests/e2e`, `tests/performance`, and `tests/stress`. Reference material and design docs live under `docs/`; generated benchmark output belongs in `performance_results/`.

## Build, Test, and Development Commands
Set up an editable environment with:
```bash
python -m venv venv && source venv/bin/activate
python -m pip install -e '.[dev]'
```
Run the API locally with `uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000`. Run all tests with `pytest`. Scope runs as needed: `pytest tests/unit -v`, `pytest tests/integration -v`, or `pytest tests/e2e/test_standard_workflow.py -v`. Format with `black src tests` and lint with `ruff check src tests`.

## Coding Style & Naming Conventions
Target Python 3.10+ and follow PEP 8 with 4-space indentation. `black` and `ruff` are the formatting and linting standards; both are configured for a 100-character line length in `pyproject.toml`. Use `snake_case` for modules, functions, variables, and test files; use `PascalCase` for classes and Pydantic models; keep route handlers and module methods small and typed. Prefer short module docstrings and explicit imports such as `from src.server.modules.project_manager import ProjectManager`.

## Testing Guidelines
Pytest is the test runner, with `asyncio_mode = auto`. Name tests `test_*.py` and keep them in the matching scope directory. Add unit tests for isolated logic changes, integration tests for API or storage flows, and e2e/performance coverage only when behavior spans phases. There is no formal coverage gate in the repo today, but every feature or bug fix should include the narrowest useful automated test.

## Commit & Pull Request Guidelines
Recent history uses short, imperative subjects such as `Implement Phase 4...`, `Fix test failures...`, and `Reorganize documentation structure...`. Follow that pattern: start with a verb, keep the subject specific, and mention the phase or subsystem when relevant. PRs should include a concise summary, affected paths, test evidence (`pytest ...` output or scope), and screenshots or sample payloads when API behavior or user-facing docs change.

## Configuration & Workspace Tips
Keep local secrets in `.env` and avoid committing virtualenv contents, local SQLite databases, or generated benchmark artifacts. Project data is stored outside the repo under `~/.vlog-editor/projects/`, so code changes should not assume checked-in runtime state.
