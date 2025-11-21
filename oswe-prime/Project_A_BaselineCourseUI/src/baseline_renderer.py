import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import html
from typing import Dict, Any

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(['html']))


def render_layout(layout: Dict[str, Any]) -> str:
    """Render baseline layout to HTML without improvements.
    The baseline intentionally uses a large hero, full-width sections, and fullscreen attachment preview.
    """
    layout_copy = dict(layout)
    # Baseline: failing fast on malformed critical inputs (simulate lack of safe fallback)
    # If tags is not a list, or instructor is not a dict, or cta is not present, raise
    tags = layout_copy.get('tags')
    if tags is not None and not isinstance(tags, list):
        raise ValueError('Baseline renderer: malformed tags')
    if 'instructor' in layout_copy and layout_copy['instructor'] is not None and not isinstance(layout_copy['instructor'], dict):
        raise ValueError('Baseline renderer: malformed instructor')
    if 'cta' not in layout_copy or layout_copy['cta'] is None:
        raise ValueError('Baseline renderer: missing cta')

    template = env.get_template('baseline_template.html')
    # sanitize strings
    sanitize_recursive(layout_copy)
    return template.render(layout=layout_copy)


def sanitize_recursive(obj: Any):
    """Escape strings in layout to avoid unsafe HTML rendering in baseline.
    Baseline is intentionally naive but should not allow script execution.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                obj[k] = html.escape(v)
            else:
                sanitize_recursive(v)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], str):
                obj[i] = html.escape(obj[i])
            else:
                sanitize_recursive(obj[i])


def compute_metrics(layout: Dict[str, Any], html_str: str) -> Dict[str, Any]:
    metrics = {}
    # hierarchy clarity: baseline is low if hero is large and no pinned card
    hero_size = layout.get('hero', {}).get('size', 'medium') if isinstance(layout.get('hero'), dict) else 'none'
    metrics['hero_size'] = hero_size
    metrics['has_pinned_info_card'] = False
    metrics['collapsible_sections'] = False

    # scroll estimate: count sections, and count long_text_size
    sections = layout.get('sections', [])
    text_lines = 0
    for s in sections:
        if isinstance(s, dict):
            text_lines += s.get('long_text_size', 0)
    metrics['estimated_scroll_lines'] = text_lines

    # mis-op risk: if cta exists and action is buy-now or enroll, and there's no confirmation
    cta = layout.get('cta', {})
    metrics['cta_action'] = cta.get('action') if isinstance(cta, dict) else None
    metrics['confirmation_present'] = False

    # Edge cases/warnings
    warnings = []
    if cta and isinstance(cta, dict) and cta.get('action') in ('buy-now', 'enroll') and not metrics['confirmation_present']:
        warnings.append('possible_misoperation_cta')
    # Long scroll detection: add a warning if scroll lines beyond a threshold
    if metrics.get('estimated_scroll_lines', 0) > 250:
        warnings.append('long_scroll')

    # If tags is a string instead of list, mark as malformed (baseline behavior)
    if isinstance(layout.get('tags', []), str):
        warnings.append('malformed_tags')
    # If tags is a list but contains non-string elements, mark mixed types
    if isinstance(layout.get('tags', []), list) and any(not isinstance(t, str) for t in layout.get('tags', [])):
        warnings.append('mixed_types')
    if any(isinstance(a, dict) and a.get('type') == 'script' for a in layout.get('attachments', [])):
        warnings.append('unsafe_attachment')

    metrics['warnings'] = warnings
    return metrics


def save_html(out_path: str, html_str: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_str)


def from_json_file(layout_json_path: str) -> Dict[str, Any]:
    with open(layout_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_long_text(size: int) -> str:
    # utility used by template via layout generated properties
    return "\n".join([f"Line {i}" for i in range(size)])


if __name__ == '__main__':
    import sys
    layout_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join('..', '..', 'shared', 'test_scenarios.json')
    scenarios = from_json_file(layout_path)
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(out_dir, exist_ok=True)
    for s in scenarios:
        layout = s['layout']
        # If sections have long_text_size, create text
        for sec in layout.get('sections', []):
            if 'long_text_size' in sec:
                sec['text'] = generate_long_text(sec['long_text_size'])
        html_out = render_layout(layout)
        out_path = os.path.join(out_dir, f"baseline_{s['id']}.html")
        save_html(out_path, html_out)
        metrics = compute_metrics(layout, html_out)
        print(f"Rendered {s['id']}, metrics: {metrics}")
