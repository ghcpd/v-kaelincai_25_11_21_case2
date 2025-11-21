import json, os

ROOT = os.path.dirname(__file__)
pre_path = os.path.join(ROOT, 'Project_A_BaselineCourseUI', 'results', 'results_pre.json')
post_path = os.path.join(ROOT, 'Project_B_EnhancedCourseUI', 'results', 'results_post.json')
out_md = os.path.join(ROOT, 'compare_report.md')
agg_json = os.path.join(ROOT, 'results_aggregated.json')

def load(p):
    if not os.path.exists(p):
        return {}
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

pre = load(pre_path)
post = load(post_path)

scenarios = sorted(set(list(pre.keys()) + list(post.keys())))

rows = []
total_delta_clarity = 0.0
count_clarity = 0
for s in scenarios:
    prem = pre.get(s, {}).get('metrics', {})
    postm = post.get(s, {}).get('metrics', {})
    pre_clarity = prem.get('hierarchy_clarity') or 0
    post_clarity = postm.get('hierarchy_clarity') or 0
    delta = post_clarity - pre_clarity
    rows.append((s, pre_clarity, post_clarity, delta, prem.get('estimated_scroll',0), postm.get('estimated_scroll',0)))
    total_delta_clarity += delta
    if post_clarity or pre_clarity:
        count_clarity += 1

avg_delta = total_delta_clarity / count_clarity if count_clarity else 0

with open(out_md, 'w', encoding='utf-8') as f:
    f.write('# Comparison Report: Baseline vs Enhanced\n\n')
    f.write('Scenarios compared: %d\n\n' % len(rows))
    f.write('| scenario | pre_clarity | post_clarity | clarity_delta | pre_scroll | post_scroll |\n')
    f.write('|---|---:|---:|---:|---:|---:|\n')
    for r in rows:
        f.write('| %s | %.3f | %.3f | %.3f | %s | %s |\n' % r)

    f.write('\n## Summary\n')
    f.write('\nAverage hierarchy clarity delta: %.3f\n' % avg_delta)
    f.write('\nDetails: For visual inspection, see generated HTML files under Project_A_BaselineCourseUI/results and Project_B_EnhancedCourseUI/results.\n')

print('compare_report.md written')
