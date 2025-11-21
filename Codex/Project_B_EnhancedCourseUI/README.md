# Project B – Enhanced Course UI

This project demonstrates the remediated course detail layout with hierarchy fixes,
persistent CTAs, collapsible blocks, and non-blocking attachment previews. The transformer
normalizes possibly malformed payloads, rebuilds a card-based layout, separates public vs.
internal narratives, and generates HTML prototypes to validate the UX delta.

## Structure
- src/layout_transformer.py – enhanced transformer and prototype builder.
- 	ests/run_scenarios.py – validation harness that enforces hierarchy, collapsibles,
  confirmation prompts, and safe preview behavior while logging metrics to
  esults/results_post.json and logs/log_post.txt.
- un_tests.sh – single entry point to execute the harness.

## Running locally
`ash
cd Project_B_EnhancedCourseUI
./run_tests.sh
`
The script provisions a venv, installs dependencies, runs every shared scenario, and produces
HTML prototypes (one per scenario) under prototypes/. These prototypes visualize the pinned
info card, modular cards, and attachment side panel.

## Metrics
- hierarchy_clarity – expected to exceed 70 through stacked cards, anchored nav, and pinned
  CTA.
- scroll_length – lowered thanks to collapsible sections and hero compression.
- mis_operation_risk – reduced because of confirmation prompts and dual CTA placement.
- edge_case_coverage & safety_score – track resilience when modules are missing or
  malformed.

## Limitations
The renderer is static HTML, attachment previews are simulated via a sidebar, and heuristics
stand in for precise analytics. The harness still captures the delta versus Project A so
regressions are obvious.