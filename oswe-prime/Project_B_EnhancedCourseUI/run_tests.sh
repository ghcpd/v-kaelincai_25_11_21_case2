#!/usr/bin/env bash
set -e
pytest -q

python - <<'PY'
import json,glob
res = {}
for path in glob.glob('results/enhanced_*.html'):
    res[path]=open(path,'r',encoding='utf-8').read()[:200]
with open('results/summary_post.json','w',encoding='utf-8') as f:
    json.dump({'pages': list(res.keys())}, f, indent=2)
print('Enhanced tests run completed')
PY
