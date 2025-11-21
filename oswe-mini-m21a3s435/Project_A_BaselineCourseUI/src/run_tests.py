import json
import argparse
import os
from transform import baseline_transform, compute_metrics


def load_scenarios(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_html(output_layout, out_file):
    # simple HTML generator visualizing the layout
    parts = []
    hero = output_layout.get('hero')
    parts.append(f"<div class=\"hero\"><h1>{hero.get('title','')}</h1></div>") if isinstance(hero, dict) else parts.append(f"<div class=\"hero\">{hero}</div>")
    parts.append("<div class=\"sections\">")
    for s in (output_layout.get('sections') or []):
        parts.append(f"<div class=\"section {s.get('type','') if isinstance(s, dict) else ''}\">{str(s)}</div>")
    parts.append("</div>")
    parts.append(f"<div class=\"cta\">{json.dumps(output_layout.get('cta'))}</div>")
    content = "\n".join(parts)
    html = f"<html><head><style>body{{font-family:Arial}}.hero{{background:#eee;padding:40px}}.section{{border-bottom:1px solid #ccc;padding:20px}}</style></head><body>{content}</body></html>"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)


def run(scenarios_path, out_dir, log_path):
    scenarios = load_scenarios(scenarios_path)
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    for s in scenarios:
        layout = s['input_layout']
        transformed, metrics = baseline_transform(layout)
        # validate expected constraints (baseline should not implement improvements)
        expected = s.get('expected', {})
        checks = []
        # baseline must not pin info card
        checks.append(('info_card_pinned', not transformed.get('ui', {}).get('info_card_pinned', False)))
        # baseline attachments should be blocking
        checks.append(('non_blocking_preview', transformed.get('ui', {}).get('attachment_preview') == 'blocking'))
        passed = all([c[1] for c in checks])
        results[s['id']] = {'status': 'passed' if passed else 'failed', 'metrics': metrics, 'checks': checks}
        # write per-scenario 'before' layout file
        with open(os.path.join(out_dir, f"{s['id']}_pre.json"), 'w', encoding='utf-8') as f:
            json.dump(layout, f, indent=2)
        with open(os.path.join(out_dir, f"{s['id']}_post.json"), 'w', encoding='utf-8') as f:
            json.dump(transformed, f, indent=2)
        # one baseline html prototype per scenario
        generate_html(layout, os.path.join(out_dir, f"{s['id']}_baseline_layout.html"))

    # write aggregated results
    with open(os.path.join(out_dir, 'results_pre.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # write log
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write('Baseline run completed for %d scenarios\n' % (len(scenarios)))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--scenarios', required=True)
    p.add_argument('--out', default='results')
    p.add_argument('--log', default='logs/log_pre.txt')
    args = p.parse_args()
    run(args.scenarios, args.out, args.log)
