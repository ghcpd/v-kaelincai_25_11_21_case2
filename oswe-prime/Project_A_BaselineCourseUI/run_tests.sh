#!/usr/bin/env bash
set -e

# Run tests and generate results
pytest -q

# Collect results
python - <<'PY'
import json,glob
res = {}
for path in glob.glob('results/*.html'):
    res[path]=open(path,'r',encoding='utf-8').read()[:200]
with open('results/summary_pre.json','w',encoding='utf-8') as f:
    json.dump({'pages': list(res.keys())}, f, indent=2)
print('Baseline tests run completed')
PY
