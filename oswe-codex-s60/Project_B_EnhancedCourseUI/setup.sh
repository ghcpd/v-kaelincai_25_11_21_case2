#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect python executable
PY_CMD=${PYTHON:-}
if command -v python >/dev/null 2>&1; then
  PY_CMD=python
elif command -v python3 >/dev/null 2>&1; then
  PY_CMD=python3
elif command -v py >/dev/null 2>&1; then
  PY_CMD="py -3"
else
  echo "Python not found. Please install Python 3." >&2
  exit 1
fi

USE_VENV=1
if [ ! -d .venv ]; then
  if ! eval "$PY_CMD -m venv .venv"; then
    echo "Warning: venv creation failed; using system Python environment." >&2
    USE_VENV=0
  fi
fi

if [ "$USE_VENV" -eq 1 ]; then
  ACTIVATE=""
  if [ -d ".venv/Scripts" ]; then
    ACTIVATE=".venv/Scripts/activate"
  elif [ -f ".venv/bin/activate" ]; then
    ACTIVATE=".venv/bin/activate"
  fi
  if [ -n "$ACTIVATE" ]; then
    # shellcheck disable=SC1091
    source "$ACTIVATE"
    PIP_CMD="pip"
  else
    echo "Warning: venv activation script not found; using system Python." >&2
    USE_VENV=0
  fi
fi

if [ "$USE_VENV" -eq 0 ]; then
  PIP_CMD="$PY_CMD -m pip"
fi

if eval "$PIP_CMD --version" >/dev/null 2>&1; then
  eval "$PIP_CMD install --upgrade pip" || true
  eval "$PIP_CMD install -r requirements.txt" || true
else
  echo "pip not available; skipping dependency installation. Ensure dependencies are present." >&2
fi
