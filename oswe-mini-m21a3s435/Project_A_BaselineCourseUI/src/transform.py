"""
Baseline transformer: performs minimal layout transformation and produces metrics for the baseline UI.
"""
import json
from html import escape


def sanitize_text(s):
    # very rudimentary sanitizer: escape HTML to neutralize script tags
    if not isinstance(s, str):
        return s
    # escape will turn < and > into safe entities (e.g. <script -> &lt;script)
    return escape(s, quote=False)


def baseline_transform(layout):
    # baseline: return layout unchanged but mark some derived fields
    output = dict(layout)
    # ensure hero not resized
    output['ui'] = output.get('ui', {})
    output['ui']['info_card_pinned'] = False
    output['ui']['collapsible_sections'] = False
    output['ui']['attachment_preview'] = 'blocking'  # full screen

    # sanitize dangerous strings
    if 'hero' in output:
        if isinstance(output['hero'], str):
            output['hero'] = sanitize_text(output['hero'])
        elif isinstance(output['hero'], dict):
            for k, v in list(output['hero'].items()):
                if isinstance(v, str):
                    output['hero'][k] = sanitize_text(v)

    # compute naive metrics
    metrics = compute_metrics(output)
    return output, metrics


def compute_metrics(layout):
    # heuristics for baseline metrics
    hero = layout.get('hero', {})
    hero_large = isinstance(hero, dict) and hero.get('large')
    image_height = isinstance(hero, dict) and hero.get('image_height', 0) or 0
    sections = layout.get('sections') or []
    total_sections = len(sections) if isinstance(sections, list) else 1
    # estimate scroll length (units arbitrary)
    scroll = 100 + (2000 if hero_large else 200) + image_height
    if isinstance(sections, list):
        for s in sections:
            if isinstance(s, dict):
                if s.get('type') == 'description':
                    content = s.get('content', '')
                    scroll += min(2000, len(str(content)))
                else:
                    scroll += 300
            else:
                scroll += 100

    metrics = {
        'hero_large': bool(hero_large),
        'estimated_scroll': scroll,
        'total_sections': total_sections,
        'collapsibles': 0,
        'attachment_preview': 'blocking',
        'misoperation_risk': 0.7  # higher in baseline
    }
    return metrics
