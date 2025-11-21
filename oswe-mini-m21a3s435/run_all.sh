#!/usr/bin/env bash
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)
echo "Running Project A (baseline)"
cd "$ROOT/Project_A_BaselineCourseUI"
./run_tests.sh
echo "Running Project B (enhanced)"
cd "$ROOT/Project_B_EnhancedCourseUI"
./run_tests.sh
cd "$ROOT"
echo "Aggregating results"
python - <<'PY'
import json, os
root = r"$ROOT"
pre = os.path.join(root, 'Project_A_BaselineCourseUI', 'results', 'results_pre.json')
post = os.path.join(root, 'Project_B_EnhancedCourseUI', 'results', 'results_post.json')
with open(pre) as f: rp = json.load(f)
with open(post) as f: ro = json.load(f)
out = {'scenarios': {}}
for k in set(list(rp.keys()) + list(ro.keys())):
    prem = rp.get(k, {}).get('metrics', {})
    postm = ro.get(k, {}).get('metrics', {})
    out['scenarios'][k] = {'pre_metrics': prem, 'post_metrics': postm}
with open(os.path.join(root, 'results_aggregated.json'), 'w') as f:
    json.dump(out, f, indent=2)
print('Written results_aggregated.json')
PY

python aggregate_results.py || true
echo "Complete. See compare_report.md and results_aggregated.json"
