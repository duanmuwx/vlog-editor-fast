#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/venv"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "Virtualenv not found. Run scripts/setup-local.sh first." >&2
  exit 1
fi

export APP_ENV="${APP_ENV:-development}"
export APP_DATA_DIR="${APP_DATA_DIR:-${HOME}/.vlog-editor}"
export SERVER_HOST="${SERVER_HOST:-0.0.0.0}"
export SERVER_PORT="${SERVER_PORT:-8000}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

mkdir -p "${APP_DATA_DIR}/projects" "${APP_DATA_DIR}/logs"

cd "${ROOT_DIR}"
exec "${VENV_DIR}/bin/python" -m uvicorn src.server.main:app --reload --host "${SERVER_HOST}" --port "${SERVER_PORT}"
