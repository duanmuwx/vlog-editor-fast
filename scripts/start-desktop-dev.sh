#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/venv"
DESKTOP_DIR="${ROOT_DIR}/vlog-editor-desktop"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "Virtualenv not found. Run scripts/setup-local.sh first." >&2
  exit 1
fi

if [[ ! -f "${DESKTOP_DIR}/package.json" ]]; then
  echo "Desktop app not found at ${DESKTOP_DIR}" >&2
  exit 1
fi

export APP_ENV="${APP_ENV:-development}"
export APP_DATA_DIR="${APP_DATA_DIR:-${HOME}/.vlog-editor}"
export SERVER_HOST="${SERVER_HOST:-0.0.0.0}"
export SERVER_PORT="${SERVER_PORT:-8000}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://127.0.0.1:${SERVER_PORT}/api}"

mkdir -p "${APP_DATA_DIR}/projects" "${APP_DATA_DIR}/logs"

BACKEND_PID=""

cleanup() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" >/dev/null 2>&1; then
    kill "${BACKEND_PID}" >/dev/null 2>&1 || true
    wait "${BACKEND_PID}" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

cd "${ROOT_DIR}"
"${VENV_DIR}/bin/python" -m uvicorn src.server.main:app --reload --host "${SERVER_HOST}" --port "${SERVER_PORT}" &
BACKEND_PID=$!

HEALTH_URL="http://127.0.0.1:${SERVER_PORT}/health"
for _ in {1..60}; do
  if "${VENV_DIR}/bin/python" -c "import urllib.request; urllib.request.urlopen('${HEALTH_URL}', timeout=2)" >/dev/null 2>&1; then
    cd "${DESKTOP_DIR}"
    npm run dev
    exit $?
  fi
  sleep 1
done

echo "Backend failed to become healthy at ${HEALTH_URL}" >&2
exit 1
