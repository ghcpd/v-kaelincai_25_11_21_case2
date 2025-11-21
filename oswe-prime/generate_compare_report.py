import json

base = json.load(open('Project_A_BaselineCourseUI/results/results_pre.json')) if __import__('os').path.exists('Project_A_BaselineCourseUI/results/results_pre.json') else {}
enh = json.load(open('Project_B_EnhancedCourseUI/results/results_post.json')) if __import__('os').path.exists('Project_B_EnhancedCourseUI/results/results_post.json') else {}

lines = []
lines.append('# Compare Report: Baseline vs Enhanced')
lines.append('')
lines.append('## Summary')

# For each scenario, compare metrics
all_ids = set(base.keys()) | set(enh.keys())
for sid in sorted(list(all_ids)):
    b = base.get(sid, {})
    e = enh.get(sid, {})
    lines.append(f'### Scenario: {sid}')
    lines.append('* Baseline warnings: ' + str(b.get('warnings')))
    lines.append('* Enhanced warnings: ' + str(e.get('warnings')))
    lines.append('* Baseline hero_size: ' + str(b.get('hero_size')))
    lines.append('* Enhanced has_pinned_info_card: ' + str(e.get('has_pinned_info_card')))
    lines.append('* Baseline scroll_lines: ' + str(b.get('estimated_scroll_lines')))
    lines.append('* Enhanced scroll reduction (lines): ' + str(e.get('estimated_scroll_lines_reduction')))
    # Add prototype links
    lines.append('* Baseline prototype: Project_A_BaselineCourseUI/results/baseline_{}.html'.format(sid))
    lines.append('* Enhanced prototype: Project_B_EnhancedCourseUI/results/enhanced_{}.html'.format(sid))
    if 'hierarchy_clarity_score' in b or 'hierarchy_clarity_score' in e:
        lines.append('* Baseline clarity: ' + str(b.get('hierarchy_clarity_score', 'N/A')))
        lines.append('* Enhanced clarity: ' + str(e.get('hierarchy_clarity_score', 'N/A')))
    lines.append('')

# Produce pass/fail matrix
lines.append('## Pass/Fail Matrix (heuristic)')
lines.append('| Scenario | Baseline | Enhanced |')
lines.append('|---|---|---|')
for sid in sorted(list(all_ids)):
    b = base.get(sid, {})
    e = enh.get(sid, {})
    b_ok = 'OK' if not b.get('warnings') else 'WARN'
    e_ok = 'OK' if not e.get('warnings') else 'WARN'
    lines.append(f'| {sid} | {b_ok} | {e_ok} |')

open('compare_report.md','w',encoding='utf-8').write('\n'.join(lines))
print('compare_report.md generated')
