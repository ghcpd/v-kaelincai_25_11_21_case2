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

bash setup.sh
# shellcheck disable=SC1091
if [ -d ".venv/Scripts" ]; then
  source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "No venv found; using system Python." >&2
fi
export PYTHONPATH="$SCRIPT_DIR/src"
mkdir -p logs results
eval "$PY_CMD tests/test_ui_transformations.py '$SCRIPT_DIR/../test_scenarios.json'"
