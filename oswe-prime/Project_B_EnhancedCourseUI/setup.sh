#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p results
mkdir -p logs

echo "Project B setup completed. Activate venv and run ./run_tests.sh"