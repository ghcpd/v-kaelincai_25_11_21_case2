#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create results and logs
mkdir -p results
mkdir -p logs

echo "Project A setup completed. Activate venv and run ./run_tests.sh"