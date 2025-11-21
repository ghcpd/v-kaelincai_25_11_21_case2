# Course Detail Page UI/UX Improvement – Baseline vs Enhanced

This repository contains two Python projects demonstrating UI/UX transformation for an online course **Detail Page**:
- **Project_A_BaselineCourseUI**: Simplistic baseline with linear layout, blocking previews, no hierarchy restructuring.
- **Project_B_EnhancedCourseUI**: Improved UI with pinned info card, collapsibles, anchored navigation, non-blocking previews, safety safeguards.

Shared artifacts:
- `test_scenarios.json` – ≥5 scenarios (normal, mis-operation, long-scroll, complex nesting, malformed input).
- `run_all.sh` – Runs both projects and generates `compare_report.md`.
- `compare_and_report.py` – Aggregates metrics and produces comparison report.
- `results/` – Aggregated outputs.

## Quickstart
```bash
bash run_all.sh
```
This will:
1. Set up virtualenvs for both projects.
2. Run their test suites.
3. Generate `compare_report.md` and collect artifacts under `results/`.

## Outputs
- **Project A**: `results/results_pre.json`, `logs/log_pre.txt`, `baseline_layout.html`.
- **Project B**: `results/results_post.json`, `logs/log_post.txt`, `enhanced_layout.html`.
- **Root**: `compare_report.md`, `results/combined_results.json` (baseline vs enhanced), copies of prototypes.

## Metrics (heuristic)
- `hierarchy_clarity` – Higher is better (anchors, pinned card, collapsibles).
- `scroll_length` – Lower is better (collapsed sections reduce length).
- `misop_risk` – Lower is better (confirmation prompts reduce risk).
- `edge_coverage` – Higher is better (handling malformed/unsafe inputs).

## Notes
- HTML prototypes are static and meant for visual inspection; metrics are simulated.
- Scripts are POSIX shell (`.sh`). On Windows, use Git Bash or WSL.
