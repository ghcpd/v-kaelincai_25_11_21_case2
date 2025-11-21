#!/usr/bin/env bash
set -e

# Run baseline project
pushd Project_A_BaselineCourseUI
./run_tests.sh
popd

# Run enhanced project
pushd Project_B_EnhancedCourseUI
./run_tests.sh
popd

# Aggregate results
python - <<'PY'
import json, os, shutil
base_path = 'Project_A_BaselineCourseUI/results/results_pre.json'
enh_path = 'Project_B_EnhancedCourseUI/results/results_post.json'
base_res = json.load(open(base_path)) if os.path.exists(base_path) else {}
enh_res = json.load(open(enh_path)) if os.path.exists(enh_path) else {}
report = {'baseline': base_res, 'enhanced': enh_res}
with open('compare_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print('Generated compare_report.json')
PY

python generate_compare_report.py

# Aggregate HTML prototypes
mkdir -p results/aggregated
cp Project_A_BaselineCourseUI/results/*.html results/aggregated/ 2>/dev/null || true
cp Project_B_EnhancedCourseUI/results/*.html results/aggregated/ 2>/dev/null || true
cp Project_A_BaselineCourseUI/results/results_pre.json results/aggregated/ 2>/dev/null || true
cp Project_B_EnhancedCourseUI/results/results_post.json results/aggregated/ 2>/dev/null || true

echo "Run all finished -- see compare_report.json and compare_report.md"
