#!/usr/bin/env bash
set -e
python -m venv .venv || python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || true
fi
echo "Project A environment ready"
