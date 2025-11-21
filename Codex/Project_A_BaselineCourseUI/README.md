# Project A – Baseline Course UI

This project simulates the overloaded course detail page prior to UX remediation. It provides
a deterministic transformer that keeps the stacked hero-first layout, blocking attachment
previews, and no mis-operation protection. Tests replay the shared 	est_scenarios.json
dataset and capture summary metrics so Project B can be compared against the exact same
inputs.

## Structure
- src/layout_transformer.py – normalizes raw payloads and emits the legacy layout model as
  well as an HTML prototype under prototypes/.
- 	ests/run_scenarios.py – custom harness that executes every scenario, validates expected
  legacy behaviors, and writes esults/results_pre.json plus logs/log_pre.txt.
- un_tests.sh – one-command entry point. It sets up a virtual environment on demand,
  installs dependencies, runs the harness, and keeps stdout minimal.

## Running locally
`ash
cd Project_A_BaselineCourseUI
./run_tests.sh
`
Outputs land in esults/ and logs/. Each scenario creates a standalone HTML prototype so
reviewers can visually inspect the baseline problems (oversized hero, no grouping, blocking
previews, etc.).

## Interpreting the metrics
- hierarchy_clarity – higher means easier to scan. Baseline numbers stay intentionally low
  due to the long, flat content stack.
- scroll_length – hero height plus an estimated 220 px per section.
- mis_operation_risk – large numbers correspond to users enrolling accidentally because
  CTA buttons lack confirmations and appear only at the footer.
- edge_case_coverage – ratio of recognized section types so we can quantify malformed inputs.

## Limitations
This is a simulation only: HTML output is static and simplified, there is no network access or
real rendering engine, and safety scoring uses heuristics. These limitations are documented so
Project B can prove measurable improvements without ambiguity.