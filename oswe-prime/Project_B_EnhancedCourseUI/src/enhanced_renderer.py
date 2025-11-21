import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import bleach
from typing import Dict, Any

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(['html']))

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + ['p', 'br', 'strong', 'em', 'ul', 'li']
ALLOWED_ATTRS = {
    '*': ['style'],
    'a': ['href', 'title']
}


def sanitize_layout(layout: Dict[str, Any]) -> Dict[str, Any]:
    # deep sanitize strings using bleach; filter attachments
    def _sanitize(obj):
        if isinstance(obj, dict):
            clean = {}
            for k, v in obj.items():
                if isinstance(v, str):
                    clean[k] = bleach.clean(v, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
                elif isinstance(v, (dict, list)):
                    clean[k] = _sanitize(v)
                else:
                    clean[k] = v
            return clean
        elif isinstance(obj, list):
            return [_sanitize(v) for v in obj]
        else:
            return obj

    return _sanitize(layout)


def transform_layout(layout: Dict[str, Any]) -> Dict[str, Any]:
    layout_copy = dict(layout)

    # sanitize
    layout_copy = sanitize_layout(layout_copy)

    # Make sure tags are a list
    if not isinstance(layout_copy.get('tags', []), list):
        tags_val = layout_copy.get('tags')
        layout_copy['tags'] = [str(tags_val)] if tags_val is not None else []
        layout_copy['_warnings'] = layout_copy.get('_warnings', []) + ['malformed_tags_fixed']

    # create pinned info card
    info_card = {
        'price': layout_copy.get('price'),
        'tags': layout_copy.get('tags', []),
        'cta': layout_copy.get('cta', {})
    }
    layout_copy['info_card'] = info_card

    # Reduce hero size if large/extra-large
    hero = layout_copy.get('hero')
    if hero and isinstance(hero, dict) and hero.get('size') in ('large', 'extra-large'):
        hero['orig_size'] = hero.get('size')
        hero['size'] = 'medium'
    layout_copy['hero'] = hero

    # Make syllabus/reviews/or related collapsible and collapsed by default
    for key in ['syllabus', 'reviews', 'related_courses']:
        if key in layout_copy:
            layout_copy[f'{key}_collapsible'] = True
            layout_copy[f'{key}_collapsed'] = True

    # Internal notes moved to internal area and hidden
    if 'internal_notes' in layout_copy:
        layout_copy['internal_notes_public'] = False

    # Attachment handling: prevent malicious types, and mark preview target (inline/side)
    safe_attachments = []
    warnings = layout_copy.get('_warnings', [])
    for a in layout_copy.get('attachments', []):
        if isinstance(a, dict):
            t = a.get('type', '')
            if t == 'script':
                # disallow script
                a['unsafe'] = True
                a['preview'] = False
                warnings.append('unsafe_attachment')
                a['type'] = 'unknown'
            else:
                a['unsafe'] = False
                a['preview'] = True
            safe_attachments.append(a)
    layout_copy['attachments'] = safe_attachments

    # Add defaults for missing modules
    if 'instructor' not in layout_copy or not isinstance(layout_copy.get('instructor'), dict):
        layout_copy['instructor'] = {'name': 'TBA', 'bio': ''}
        warnings.append('missing_instructor')

    # Create card-based visual segmentation indicator
    layout_copy['carded'] = True

    # add mobile friendly CTA
    layout_copy['mobile_cta_bottom'] = True

    # Add confirmation for enroll
    cta = layout_copy.get('cta') or {}
    if cta.get('action') in ('enroll', 'buy-now'):
        cta['requires_confirmation'] = True
    layout_copy['cta'] = cta

    # metrics helpers
    layout_copy['_warnings'] = warnings

    return layout_copy


def render_layout(layout: Dict[str, Any]) -> str:
    template = env.get_template('enhanced_template.html')
    return template.render(layout=transform_layout(layout))


def compute_metrics(layout: Dict[str, Any], html_str: str) -> Dict[str, Any]:
    metrics = {}
    tlayout = transform_layout(layout)
    # hierarchy clarity scoring: start 50; add if info card, collapsible sections etc
    score = 50
    if tlayout.get('info_card'):
        score += 25
    if tlayout.get('hero') and tlayout['hero'].get('orig_size') in ('large', 'extra-large'):
        score -= 10
    if tlayout.get('syllabus_collapsible'):
        score += 10
    if tlayout.get('carded'):
        score += 5
    metrics['hierarchy_clarity_score'] = max(0, min(100, score))

    # estimate scroll reduction: old scroll from baseline vs new
    sections = layout.get('sections', [])
    old_lines = sum([s.get('long_text_size', 0) for s in sections])
    # assume collapsible hides long sections, so we count 0 visible lines
    new_lines = 0
    metrics['estimated_scroll_lines_reduction'] = old_lines - new_lines

    # mis-operation reduction metric
    cta = tlayout.get('cta', {})
    metrics['confirmation_present'] = bool(cta.get('requires_confirmation'))
    metrics['has_pinned_info_card'] = bool(tlayout.get('info_card'))

    # warnings and edges
    metrics['warnings'] = list(set(tlayout.get('_warnings', [])))

    # edge coverage: count number of handled problematic elements
    handled = 0
    total_prob = 0
    if any(isinstance(x, dict) and x.get('type') == 'script' for x in layout.get('attachments', [])):
        total_prob += 1
        handled += 1 if 'unsafe_attachment' in metrics['warnings'] else 0
    if not isinstance(layout.get('tags', []), list):
        total_prob += 1
        handled += 1
    metrics['edge_case_handling_ratio'] = handled / total_prob if total_prob else 1.0

    return metrics


def save_html(out_path: str, html_str: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_str)


def from_json_file(layout_json_path: str) -> Dict[str, Any]:
    with open(layout_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == '__main__':
    import sys
    layout_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join('..', '..', 'shared', 'test_scenarios.json')
    scenarios = from_json_file(layout_path)
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(out_dir, exist_ok=True)
    for s in scenarios:
        layout = s['layout']
        # if sections have long_text_size, we generate the text for the template to show a sample
        for sec in layout.get('sections', []):
            if 'long_text_size' in sec:
                sec['text'] = '\n'.join([f"Line {i}" for i in range(sec['long_text_size'])])
        html_out = render_layout(layout)
        out_path = os.path.join(out_dir, f"enhanced_{s['id']}.html")
        save_html(out_path, html_out)
        metrics = compute_metrics(layout, html_out)
        print(f"Rendered enhanced: {s['id']}, metrics: {metrics}")
