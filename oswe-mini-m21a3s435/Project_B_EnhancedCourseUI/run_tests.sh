#!/usr/bin/env bash
set -e
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT_DIR"
if [ ! -d .venv ]; then
  ./setup.sh
fi
. .venv/bin/activate || true
python src/run_tests.py --scenarios ../../test_scenarios.json --out results --log logs/log_post.txt
echo "Enhanced tests finished. See results/ and logs/"
