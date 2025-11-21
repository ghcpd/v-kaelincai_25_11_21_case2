import os
import json
import pytest
from pathlib import Path

from src.baseline_renderer import render_layout, compute_metrics, save_html, from_json_file

ROOT = Path(__file__).parent.parent
SCENARIOS_FILE = ROOT.parent / 'shared' / 'test_scenarios.json'
RESULTS_DIR = ROOT.parent / 'results'
LOGS_DIR = ROOT.parent / 'logs'

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


@pytest.mark.parametrize('scenario', range(0, 5))
def test_baseline_scenarios(scenario):
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
        save_html(str(RESULTS_DIR / f"baseline_{s['id']}.html"), html_out)
        with open(LOGS_DIR / f"log_{s['id']}.txt", 'w', encoding='utf-8') as f:
            f.write(json.dumps({'metrics': metrics}, indent=2))
    except Exception as e:
        # For baseline, if we can't render, mark as error and assert expectations
        metrics = {'error': str(e)}
        with open(LOGS_DIR / f"log_{s['id']}.txt", 'w', encoding='utf-8') as f:
            f.write(json.dumps({'metrics': metrics}, indent=2))
        assert s['expectations']['should_render'] is False
        return

    # Basic assertions according to baseline expectations
    if not s['expectations']['should_render']:
        pytest.fail('Expected rendering to fail for malformed input')

    # Check specific warning expectations
    expected_warnings = s['expectations'].get('warnings', [])
    for w in expected_warnings:
        assert w in metrics.get('warnings', []), f"Expected warning {w} in scenario {s['id']}"

    # Baseline should not have collapsible sections and pinned info
    assert metrics.get('collapsible_sections') is False
    assert metrics.get('has_pinned_info_card') is False

    # Save per-scenario results
    agg_file = RESULTS_DIR / 'results_pre.json'
    if agg_file.exists():
        agg = json.load(open(agg_file, 'r', encoding='utf-8'))
    else:
        agg = {}
    agg[s['id']] = metrics
    with open(agg_file, 'w', encoding='utf-8') as f:
        json.dump(agg, f, indent=2)
