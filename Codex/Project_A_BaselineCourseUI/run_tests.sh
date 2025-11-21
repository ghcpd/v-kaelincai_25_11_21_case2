#!/usr/bin/env bash
set -euo pipefail
find_python() {
  for candidate in python python3 py python.exe py.exe; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}
if ! PYTHON_BIN=$(find_python); then
  echo "Python interpreter not found." >&2
  exit 1
fi
if [ ! -d .venv ]; then
  "${PYTHON_BIN}" -m venv .venv
fi
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
elif [ -f .venv/Scripts/activate ]; then
  # shellcheck disable=SC1091
  source .venv/Scripts/activate
else
  echo "Virtual environment activation script not found." >&2
  exit 1
fi
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null
python tests/run_scenarios.py
