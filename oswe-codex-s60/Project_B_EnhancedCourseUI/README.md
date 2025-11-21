# Project B – Enhanced Course UI

Improved UI/UX transformation for the Online Course **Detail Page** with hierarchy restructuring, collapsibles, pinned info card, non-blocking previews, and safety safeguards.

## Key Improvements
- **Pinned info card** (sticky sidebar, mobile bottom CTA)
- **Collapsible** syllabus/reviews/related sections
- **Anchored navigation** for scannability
- **Non-blocking attachment previews** (side panel)
- **Public vs internal separation** (hidden instructor notes)
- **Confirmation prompts** for enroll/pay actions
- **Safe degradation** for malformed layouts & unsafe URLs (sanitized)

## Contents
- `src/transformer.py` – Restructures layout, pins info card, separates internal notes, sets collapsibles, safe fallbacks.
- `src/metrics.py` – Heuristic metrics reflecting improvements (clarity, scroll length reduction, mis-op risk, edge coverage).
- `src/html_generator.py` – Generates `enhanced_layout.html` with sticky sidebar, `<details>` collapsibles, side preview panel, mobile CTA.
- `tests/test_ui_transformations.py` – Loads `../test_scenarios.json`, runs transformations, computes metrics, writes `results/results_post.json` and `logs/log_post.txt`.
- `run_tests.sh` – One-command execution (sets up venv, runs tests, generates prototype).
- `requirements.txt`, `setup.sh` – Environment setup.

## Usage
```bash
bash run_tests.sh
```
Outputs:
- `results/results_post.json` – Per-scenario outcomes & metrics.
- `logs/log_post.txt` – Execution log.
- `enhanced_layout.html` and `results/enhanced_layout.html` – Enhanced HTML prototype for visual inspection.

## Interpretation
- **Hierarchy clarity** gains from anchors, pinned card, collapsibles.
- **Scroll length** reduced by default-collapsed sections.
- **Mis-operation risk** lowered via confirmation prompts.
- **Edge coverage** improves by sanitization and safe fallback.

## Scenarios & Pitfalls
- **Long-scroll**: Collapsibles significantly reduce estimated scroll.
- **Mis-operation**: Confirmation prompts applied to CTAs/actions.
- **Complex nesting**: Attachments preview in side panel; unsafe URLs sanitized.
- **Malformed input**: Auto-repairs missing ids/types; safe fallback prevents crashes.

## Limitations
- Simulated metrics; not pixel-perfect.
- Side panel previews rely on browser iframe restrictions for remote content.
- Internal notes are present but hidden; no authentication simulated.
