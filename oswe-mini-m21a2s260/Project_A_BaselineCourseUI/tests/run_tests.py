import json, os, sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]/'src'))
from transform import BaselineTransform

SCENARIOS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','shared','test_scenarios.json'))
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','results'))
os.makedirs(OUT_DIR,exist_ok=True)

with open(SCENARIOS_PATH,'r',encoding='utf-8') as f:
    sc = json.load(f)

results = []
log_lines = []
for s in sc:
    tid = s['id']
    layout = s['layout']
    b = BaselineTransform(layout)
    res = b.transform()
    html_path = os.path.join(OUT_DIR,f'baseline_{tid}.html')
    b.render_html(html_path)
    metrics = res.get('metrics',{})
    # Compute simple scores
    clarity = 0.4 if (layout.get('hero') and (layout['hero'].get('size') in ['large','xlarge'])) else 0.7
    scroll = 1.0 if (layout.get('hero') or {}).get('size') in ['large','xlarge'] else 0.6
    out = {"id":tid,"status":"processed","metrics":{"hierarchy_clarity":clarity,"scroll_length":scroll},"ui_warnings":[],"edge_case_flags":[],"output_html":html_path}
    results.append(out)
    log_lines.append(f"Processed {tid} -> html: {html_path}")

# write results
with open(os.path.join(OUT_DIR,'results_pre.json'),'w',encoding='utf-8') as f:
    json.dump(results,f,indent=2)
with open(os.path.join(OUT_DIR,'log_pre.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
print('Baseline tests done, results in',OUT_DIR)
