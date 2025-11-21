#!/usr/bin/env bash
set -e
BASE_DIR=$(pwd)
echo Running baseline tests
bash Project_A_BaselineCourseUI/run_tests.sh
echo Running enhanced tests
bash Project_B_EnhancedCourseUI/run_tests.sh
# Aggregate and compare
python - <<'PY'
import json,os
base='results/results_pre.json'
post='results/results_post.json'
if not os.path.exists(base):
    print('Baseline results missing')
    base=None
if not os.path.exists(post):
    print('Post results missing')
    post=None
b= json.load(open(base)) if base else []
p= json.load(open(post)) if post else []
# compute deltas
rows=[]
for bi,pi in zip(b,p):
    rows.append({
        'id':bi['id'],
        'pre_clarity':bi['metrics']['hierarchy_clarity'],
        'post_clarity':pi['metrics']['hierarchy_clarity'],
        'delta_clarity':pi['metrics']['hierarchy_clarity'] - bi['metrics']['hierarchy_clarity'],
        'pre_scroll':bi['metrics']['scroll_length'],'post_scroll':pi['metrics']['scroll_length'],'delta_scroll':bi['metrics']['scroll_length']-pi['metrics']['scroll_length']
    })
open('compare_report.md','w').write('# Comparison Report\n\n'+json.dumps(rows,indent=2))
print('Comparison report written to compare_report.md')
PY
