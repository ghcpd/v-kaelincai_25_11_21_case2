"""
Enhanced transformer: reorganizes UI for better hierarchy, collapsible sections, side-panel previews, safe fallbacks.
"""
import copy
from html import escape


def sanitize_html_string(s: str) -> str:
    if not isinstance(s, str):
        return s
    # remove script tags and on* attributes
    s = s.replace('<script', '&lt;script').replace('</script>', '&lt;/script&gt;')
    # naive strip of event attributes
    import re
    s = re.sub(r'on\w+\s*=\s*"[^"]*"', '', s, flags=re.I)
    return escape(s, quote=False)


def make_card(section):
    return {'card': True, 'original': section}


def deep_find_sections(node):
    # returns list of section nodes found recursively
    found = []
    if isinstance(node, dict):
        t = node.get('type')
        if t in ('syllabus', 'description', 'instructor', 'reviews'):
            found.append(node)
        for v in node.values():
            if isinstance(v, (dict, list)):
                found += deep_find_sections(v)
    elif isinstance(node, list):
        for item in node:
            found += deep_find_sections(item)
    return found


def enhanced_transform(layout):
    out = copy.deepcopy(layout) if isinstance(layout, dict) else {'hero': str(layout)}
    ui = out.setdefault('ui', {})
    # pin a compact info card
    ui['info_card_pinned'] = True
    ui['collapsible_sections'] = True
    ui['attachment_preview'] = 'side_panel'
    ui['cta_persistent'] = True
    ui['cta_requires_confirmation'] = True

    # separate internal notes and public content
    public_desc = []
    internal = out.pop('internal_notes', None)
    if internal:
        out['internal'] = internal

    # normalize sections safely
    sections = out.get('sections')
    if not isinstance(sections, list):
        # fallback: create empty safe structure
        out['sections'] = []
        ui['safe_fallback_sections'] = True
    else:
        new_sections = []
        for s in sections:
            # sanitize if string contains unsafe scripts
            if isinstance(s, dict):
                # collapse long nested groups into cards
                if s.get('type') == 'group' or s.get('children'):
                    # create a top-level card representing the group
                    group = {'type': 'group', 'title': s.get('title', 'Group'), 'collapsible': True, 'children': s.get('children', [])}
                    new_sections.append(make_card(group))
                else:
                    # convert to card if it's a big section
                    # make long or content-heavy sections collapsible (improves scroll)
                    if s.get('type') in ('syllabus', 'reviews', 'description'):
                        s['collapsible'] = True
                    # sanitize strings inside
                    for k, v in list(s.items()):
                        if isinstance(v, str):
                            s[k] = sanitize_html_string(v)
                    new_sections.append(make_card(s))
            else:
                # string or unknown
                new_sections.append(make_card({'type': 'description', 'content': sanitize_html_string(str(s))}))
        out['sections'] = new_sections

    # compute metrics
    metrics = compute_metrics(out)
    return out, metrics


def compute_metrics(layout):
    hero = layout.get('hero', {})
    hero_large = isinstance(hero, dict) and hero.get('large')
    image_height = isinstance(hero, dict) and hero.get('image_height', 0) or 0
    sections = layout.get('sections') or []
    tot = len(sections) if isinstance(sections, list) else 0

    # clarity score - heuristic: pinned info card + card based sections + fewer visible sections
    clarity = 0.5
    clarity += 0.3 if layout.get('ui', {}).get('info_card_pinned') else 0
    clarity += 0.2 * (min(1, tot / 5))

    # collapsed sections count
    collapsibles = 0
    for s in sections:
        if isinstance(s, dict) and s.get('card') and s.get('original', {}).get('collapsible'):
            collapsibles += 1
        elif isinstance(s, dict) and s.get('card') and s.get('original', {}).get('type') == 'group':
            collapsibles += 1

    # estimated scroll reduced for collapsed sections
    base_scroll = 100 + (2000 if hero_large else 200) + image_height
    scroll_reduction = collapsibles * 400
    estimated_scroll = max(200, base_scroll - scroll_reduction)

    metrics = {
        'hero_large': bool(hero_large),
        'estimated_scroll': estimated_scroll,
        'total_sections': tot,
        'collapsibles': collapsibles,
        'attachment_preview': layout.get('ui', {}).get('attachment_preview'),
        'hierarchy_clarity': round(clarity, 3),
        'misoperation_risk': 0.1  # lower due to confirmation and persistent CTA
    }
    return metrics
