#!/usr/bin/env python3
"""Aggregates baseline vs enhanced results and creates a markdown report."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
BASE_RESULTS = ROOT / "Project_A_BaselineCourseUI" / "results" / "results_pre.json"
ENH_RESULTS = ROOT / "Project_B_EnhancedCourseUI" / "results" / "results_post.json"
AGG_RESULTS = ROOT / "results" / "aggregate_results.json"
REPORT_PATH = ROOT / "compare_report.md"


def load_payload(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def compute_scenario_deltas(pre: Dict, post: Dict) -> List[Dict]:
    index_pre = {item["id"]: item for item in pre["scenarios"]}
    index_post = {item["id"]: item for item in post["scenarios"]}
    all_ids = sorted(set(index_pre) | set(index_post))
    rows: List[Dict] = []
    for scenario_id in all_ids:
        pre_entry = index_pre.get(scenario_id)
        post_entry = index_post.get(scenario_id)
        if not pre_entry or not post_entry:
            continue
        pre_metrics = pre_entry.get("metrics", {})
        post_metrics = post_entry.get("metrics", {})
        delta_hierarchy = round(post_metrics.get("hierarchy_clarity", 0) - pre_metrics.get("hierarchy_clarity", 0), 2)
        delta_scroll = round(pre_metrics.get("scroll_length", 0) - post_metrics.get("scroll_length", 0), 2)
        delta_mis = round(pre_metrics.get("mis_operation_risk", 0) - post_metrics.get("mis_operation_risk", 0), 2)
        delta_edge = round(post_metrics.get("edge_case_coverage", 0) - pre_metrics.get("edge_case_coverage", 0), 2)
        rows.append(
            {
                "id": scenario_id,
                "baseline_status": pre_entry.get("status"),
                "enhanced_status": post_entry.get("status"),
                "hierarchy_delta": delta_hierarchy,
                "scroll_delta": delta_scroll,
                "mis_operation_delta": delta_mis,
                "edge_case_delta": delta_edge,
                "baseline_proto": pre_entry.get("prototype_path"),
                "enhanced_proto": post_entry.get("prototype_path"),
            }
        )
    return rows


def write_report(rows: List[Dict], pre_summary: Dict, post_summary: Dict) -> None:
    avg_hierarchy_gain = round(sum(r["hierarchy_delta"] for r in rows) / len(rows), 2)
    avg_scroll_reduction = round(sum(r["scroll_delta"] for r in rows) / len(rows), 2)
    avg_mis_reduction = round(sum(r["mis_operation_delta"] for r in rows) / len(rows), 2)
    avg_edge_gain = round(sum(r["edge_case_delta"] for r in rows) / len(rows), 2)
    lines = [
        "# Comparison Report",
        "",
        "## Pass/Fail Matrix",
        "| Scenario | Baseline | Enhanced |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['id']} | {row['baseline_status']} | {row['enhanced_status']} |")
    lines.extend([
        "",
        "## Hierarchy & Scroll Improvements",
        f"- Average hierarchy clarity gain: {avg_hierarchy_gain}",
        f"- Average scroll-length reduction: {avg_scroll_reduction} px",
        f"- Average mis-operation risk reduction: {avg_mis_reduction}",
        f"- Average edge-case coverage delta: {avg_edge_gain} pts",
        "",
        "## Attachment Preview & Interaction Safety",
        "- Baseline preview mode: overlay (blocking); Enhanced: side-panel with inline fallback.",
        "- Confirmation prompts added for enrollment/payment plus sticky mobile CTA.",
        "",
        "## Prototype References",
    ])
    for row in rows:
        lines.append(f"- {row['id']}: baseline -> {row['baseline_proto']}, enhanced -> {row['enhanced_proto']}")
    lines.extend([
        "",
        "## Summaries",
        f"- Baseline pass rate: {pre_summary.get('passed')}/{pre_summary.get('total_scenarios')}",
        f"- Enhanced pass rate: {post_summary.get('passed')}/{post_summary.get('total_scenarios')}",
        f"- Baseline avg hierarchy clarity: {pre_summary.get('average_hierarchy_clarity')}",
        f"- Enhanced avg hierarchy clarity: {post_summary.get('average_hierarchy_clarity')}",
        f"- Baseline avg scroll length: {pre_summary.get('average_scroll_length')}",
        f"- Enhanced avg scroll length: {post_summary.get('average_scroll_length')}",
    ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    pre = load_payload(BASE_RESULTS)
    post = load_payload(ENH_RESULTS)
    rows = compute_scenario_deltas(pre, post)
    aggregate_payload = {"scenarios": rows, "baseline_summary": pre["summary"], "enhanced_summary": post["summary"]}
    AGG_RESULTS.write_text(json.dumps(aggregate_payload, indent=2), encoding="utf-8")
    write_report(rows, pre["summary"], post["summary"])


if __name__ == "__main__":
    main()