#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_DIR="${ROOT_DIR}/vlog-editor-desktop"
RUNTIME_ROOT="${DESKTOP_DIR}/backend-runtime"
APP_DIR="${RUNTIME_ROOT}/app"
VENV_DIR="${RUNTIME_ROOT}/venv"
TARGET_PLATFORM="${1:-linux}"

if [[ ! -d "${DESKTOP_DIR}" ]]; then
  echo "Desktop directory not found: ${DESKTOP_DIR}" >&2
  exit 1
fi

if [[ "${TARGET_PLATFORM}" != "linux" && "${TARGET_PLATFORM}" != "mac" && "${TARGET_PLATFORM}" != "darwin" ]]; then
  echo "Unsupported target platform: ${TARGET_PLATFORM}" >&2
  exit 1
fi

rm -rf "${RUNTIME_ROOT}"
mkdir -p "${APP_DIR}"

tar -C "${ROOT_DIR}" \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='.ruff_cache' \
  --exclude='tests' \
  --exclude='performance_results' \
  --exclude='vlog-editor-desktop' \
  -cf - \
  pyproject.toml README.md src \
  | tar -C "${APP_DIR}" -xf -

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel
"${VENV_DIR}/bin/pip" install "${APP_DIR}"

cat <<EOF
Prepared desktop backend runtime at:
  ${RUNTIME_ROOT}
EOF
