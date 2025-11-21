# Project A – Baseline Course UI

Simplistic baseline implementation for the Online Course **Detail Page**. It preserves the original layout with no hierarchy restructuring, no collapsibles, blocking attachment previews, and no mis-operation protections.

## Contents
- `src/transformer.py` – Minimal normalization; pass-through layout.
- `src/metrics.py` – Heuristic metrics (hierarchy clarity, scroll length, mis-op risk, edge coverage).
- `src/html_generator.py` – Generates `baseline_layout.html` (linear, full-width sections, blocking preview modal).
- `tests/test_ui_transformations.py` – Loads `../test_scenarios.json`, runs transformations, computes metrics, writes `results/results_pre.json` and `logs/log_pre.txt`.
- `run_tests.sh` – One-command execution (sets up venv, runs tests, generates prototype).
- `requirements.txt`, `setup.sh` – Environment setup.

## Usage
```bash
bash run_tests.sh
```
Outputs:
- `results/results_pre.json` – Per-scenario outcomes & metrics.
- `logs/log_pre.txt` – Execution log.
- `baseline_layout.html` and `results/baseline_layout.html` – Baseline HTML prototype for visual inspection.

## Interpretation
- **Hierarchy clarity** is low due to oversized hero and unpinned info card.
- **Scroll length** is high because all sections are expanded linearly.
- **Mis-operation risk** flags dangerous actions without confirmation.
- **Edge coverage** is minimal (only minimal normalization).

## Scenarios & Pitfalls
- **Normal/long-scroll**: Expect high scroll length, low clarity.
- **Mis-operation**: No confirmation prompts; risk remains high.
- **Complex nesting**: Layout is rendered flatly; attachment previews block context.
- **Malformed input**: Minimal normalization avoids crashes but no robust safe fallbacks.

## Limitations
- Simulated rendering/metrics are heuristic, not pixel-accurate.
- No sanitization beyond Jinja2 auto-escape; unsafe URLs are not filtered.
- No mobile optimizations or anchored navigation.
