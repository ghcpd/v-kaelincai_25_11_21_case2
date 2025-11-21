import os
import json
import pytest
from pathlib import Path

from src.enhanced_renderer import render_layout, compute_metrics, save_html, transform_layout, from_json_file

ROOT = Path(__file__).parent.parent
SCENARIOS_FILE = ROOT.parent / 'shared' / 'test_scenarios.json'
RESULTS_DIR = ROOT.parent / 'results'
LOGS_DIR = ROOT.parent / 'logs'

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


@pytest.mark.parametrize('scenario', range(0, 5))
def test_enhanced_scenarios(scenario):
    scenarios = from_json_file(str(SCENARIOS_FILE))
    s = scenarios[scenario]
    layout = s['layout']
    # convert long_text_size
    for sec in layout.get('sections', []):
        if 'long_text_size' in sec:
            sec['text'] = '\n'.join([f"Line {i}" for i in range(sec['long_text_size'])])
    try:
        html_out = render_layout(layout)
        metrics = compute_metrics(layout, html_out)
        save_html(str(RESULTS_DIR / f"enhanced_{s['id']}.html"), html_out)
        with open(LOGS_DIR / f"log_enhanced_{s['id']}.txt", 'w', encoding='utf-8') as f:
            f.write(json.dumps({'metrics': metrics}, indent=2))
    except Exception as e:
        metrics = {'error': str(e)}
        with open(LOGS_DIR / f"log_enhanced_{s['id']}.txt", 'w', encoding='utf-8') as f:
            f.write(json.dumps({'metrics': metrics}, indent=2))
        assert False, f"Enhanced renderer raised exception {e}"

    # Validate enhanced properties
    assert metrics.get('hierarchy_clarity_score') >= 50
    assert metrics.get('has_pinned_info_card') is True
    # Confirm badges
    if s['id'] == 'mis_operation_flow':
        # misoperation should be reduced via confirmation
        assert metrics.get('confirmation_present') is True
    # attachments safe
    if 'attachments' in layout and any(isinstance(a, dict) and a.get('type') == 'script' for a in layout.get('attachments', [])):
        assert 'unsafe_attachment' in metrics.get('warnings', [])

    # Save per-scenario results file
    agg_file = RESULTS_DIR / 'results_post.json'
    if agg_file.exists():
        agg = json.load(open(agg_file, 'r', encoding='utf-8'))
    else:
        agg = {}
    agg[s['id']] = metrics
    with open(agg_file, 'w', encoding='utf-8') as f:
        json.dump(agg, f, indent=2)
