#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

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

echo "Running baseline (Project A)..."
bash "$ROOT/Project_A_BaselineCourseUI/run_tests.sh"

echo "Running enhanced (Project B)..."
bash "$ROOT/Project_B_EnhancedCourseUI/run_tests.sh"

echo "Generating comparison report..."
eval "$PY_CMD '$ROOT/compare_and_report.py'"

# Aggregate artifacts into root/results for convenience
mkdir -p "$ROOT/results"
cp -f "$ROOT/Project_A_BaselineCourseUI/results/results_pre.json" "$ROOT/results/" || true
cp -f "$ROOT/Project_B_EnhancedCourseUI/results/results_post.json" "$ROOT/results/" || true
cp -f "$ROOT/Project_A_BaselineCourseUI/baseline_layout.html" "$ROOT/results/" || true
cp -f "$ROOT/Project_B_EnhancedCourseUI/enhanced_layout.html" "$ROOT/results/" || true

echo "Done. See compare_report.md and results/."
