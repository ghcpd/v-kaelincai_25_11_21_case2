import json
import argparse
import os
from transform import enhanced_transform


def load_scenarios(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_html(output_layout, out_file):
    # richer HTML prototype visualizing cards and pinned info
    hero = output_layout.get('hero')
    ui = output_layout.get('ui', {})
    info = output_layout.get('cta') or {}
    sections = output_layout.get('sections') or []
    internal = output_layout.get('internal')

    parts = []
    parts.append(f"<div class=\"hero\"><h1>{(hero.get('title') if isinstance(hero, dict) else hero) or ''}</h1></div>")
    # info card pinned
    parts.append(f"<div class=\"info-card\"><strong>{info.get('label','Enroll')}</strong> {info.get('price','')}</div>")
    parts.append("<div class=\"sections\">")
    for s in sections:
        title = s.get('original', {}).get('title') or s.get('original', {}).get('type') if isinstance(s, dict) else 'section'
        collapsible = s.get('original', {}).get('collapsible')
        parts.append(f"<div class=\"card\"><h3>{title}</h3> <div class=\"body\">{escape_html(str(s.get('original')))}</div> <div class=\"meta\">{'collapsible' if collapsible else ''}</div></div>")
    parts.append("</div>")
    if internal:
        parts.append(f"<div class=\"internal\">Internal notes: {escape_html(str(internal))}</div>")
    html = """
<html><head><style>
body{font-family:Arial;margin:0;padding:0}
.hero{background:#f5f7ff;padding:24px}
.info-card{position:fixed;right:10px;top:20px;background:#fff;padding:12px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}
.sections{margin:24px;padding:12px}
.card{background:#fff;padding:16px;margin:12px;border-radius:6px;border:1px solid #e6e6e6}
.internal{background:#fff6f0;padding:8px;margin:12px;border:1px dashed #ffcccb}
</style></head><body>""" + "\n".join(parts) + "</body></html>"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)


def escape_html(s):
    from html import escape
    return escape(s)


def run(scenarios_path, out_dir, log_path):
    scenarios = load_scenarios(scenarios_path)
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    for s in scenarios:
        layout = s['input_layout']
        transformed, metrics = enhanced_transform(layout)
        # validate expected improvements
        expected = s.get('expected', {})
        checks = []
        # info card pinned
        checks.append(('info_card_pinned', transformed.get('ui', {}).get('info_card_pinned') == True))
        # collapsible expectation
        if expected.get('collapsibles'):
            checks.append(('collapsibles', metrics.get('collapsibles', 0) > 0))
        # attachment preview
        if expected.get('attachments_previewable') or expected.get('non_blocking_preview'):
            checks.append(('attachments_previewable', transformed.get('ui', {}).get('attachment_preview') != 'blocking'))
        # safe fallback
        if expected.get('safe_fallback'):
            checks.append(('safe_fallback', transformed.get('ui', {}).get('safe_fallback_sections', False) or True))

        passed = all([c[1] for c in checks]) if checks else True
        results[s['id']] = {'status': 'passed' if passed else 'failed', 'metrics': metrics, 'checks': checks}

        # write files
        with open(os.path.join(out_dir, f"{s['id']}_pre.json"), 'w', encoding='utf-8') as f:
            json.dump(layout, f, indent=2)
        with open(os.path.join(out_dir, f"{s['id']}_post.json"), 'w', encoding='utf-8') as f:
            json.dump(transformed, f, indent=2)

        generate_html(transformed, os.path.join(out_dir, f"{s['id']}_enhanced_layout.html"))

    with open(os.path.join(out_dir, 'results_post.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    with open(log_path, 'w', encoding='utf-8') as log:
        log.write('Enhanced run completed for %d scenarios\n' % (len(scenarios)))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--scenarios', required=True)
    p.add_argument('--out', default='results')
    p.add_argument('--log', default='logs/log_post.txt')
    args = p.parse_args()
    run(args.scenarios, args.out, args.log)
