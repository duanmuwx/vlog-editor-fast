#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/venv"
APP_DATA_DIR="${APP_DATA_DIR:-${HOME}/.vlog-editor}"

require_command() {
  local command_name="$1"
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    exit 1
  fi
}

require_command python3
require_command node
require_command npm
require_command ffmpeg

mkdir -p "${APP_DATA_DIR}/projects" "${APP_DATA_DIR}/logs"

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -e '.[dev]'

if [[ -f "${ROOT_DIR}/vlog-editor-desktop/package.json" ]]; then
  npm --prefix "${ROOT_DIR}/vlog-editor-desktop" install
fi

cat <<EOF
Local setup complete.

Backend:
  ${ROOT_DIR}/scripts/start-backend.sh

Desktop dev:
  ${ROOT_DIR}/scripts/start-desktop-dev.sh
EOF
