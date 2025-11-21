#!/usr/bin/env python3
"""Runs enhanced layout tests and produces metrics/logs."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from layout_transformer import EnhancedCourseLayoutTransformer  # type: ignore  # noqa: E402


class EnhancedValidator:
    def validate(self, layout_result, scenario: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        layout = layout_result.layout
        metrics = layout_result.metrics
        expectations = scenario.get("expectations", {})
        required_metrics = expectations.get("required_metrics", [])
        for metric in required_metrics:
            if metric == "errors":
                if not layout_result.errors:
                    errors.append("Missing metric: errors")
                continue
            if metric not in metrics:
                errors.append(f"Missing metric: {metric}")
        if not layout.get("pinned_info_card"):
            errors.append("Pinned info card missing")
        if not layout.get("cta", {}).get("persistent"):
            errors.append("CTA should be persistent in enhanced version")
        if not layout.get("collapsible_sections"):
            errors.append("Collapsible sections must be enabled")
        preview = layout.get("attachment_preview", {})
        if preview.get("blocking"):
            errors.append("Attachment preview must be non-blocking")
        if "confirmations" not in layout.get("mis_operation_prevention", {}):
            errors.append("Missing confirmation prompts")
        if metrics.get("hierarchy_clarity", 0) < 70:
            errors.append("Hierarchy clarity should exceed 70")
        if metrics.get("mis_operation_risk", 100) > 40:
            errors.append("Mis-operation risk should be low")
        status = "passed" if not errors else "failed"
        return {"status": status, "errors": errors}


def load_scenarios() -> List[Dict[str, Any]]:
    scenario_path = Path(__file__).resolve().parents[2] / "test_scenarios.json"
    with scenario_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    transformer = EnhancedCourseLayoutTransformer(project_root / "prototypes")
    scenarios = load_scenarios()
    validator = EnhancedValidator()
    scenario_results: List[Dict[str, Any]] = []
    log_lines: List[str] = []
    failures = 0
    start = time.time()
    for scenario in scenarios:
        try:
            layout_result = transformer.transform(scenario)
            validation = validator.validate(layout_result, scenario)
            status = layout_result.status
            if validation["status"] == "failed":
                status = "failed"
                failures += 1
            scenario_results.append(
                {
                    "id": scenario["id"],
                    "status": status,
                    "metrics": layout_result.metrics,
                    "ui_warnings": layout_result.ui_warnings,
                    "edge_case_flags": layout_result.edge_case_flags,
                    "errors": list(layout_result.errors) + validation["errors"],
                    "prototype_path": layout_result.prototype_path,
                }
            )
            log_lines.append(
                f"[{scenario['id']}] status={status} hierarchy={layout_result.metrics.get('hierarchy_clarity')} "
                f"scroll={layout_result.metrics.get('scroll_length')} collapsible={len(layout_result.layout.get('collapsible_sections', []))}"
            )
        except Exception as exc:  # pragma: no cover
            failures += 1
            scenario_results.append(
                {
                    "id": scenario.get("id", "unknown"),
                    "status": "error",
                    "metrics": {},
                    "ui_warnings": ["execution_error"],
                    "edge_case_flags": ["crash"],
                    "errors": [str(exc)],
                    "prototype_path": "",
                }
            )
            log_lines.append(f"[{scenario.get('id', 'unknown')}] crashed: {exc}")
    duration = time.time() - start
    summary = {
        "total_scenarios": len(scenarios),
        "passed": len(scenarios) - failures,
        "failed": failures,
        "average_hierarchy_clarity": round(mean(
            [r["metrics"].get("hierarchy_clarity", 0) for r in scenario_results if r["metrics"]]
        ), 2) if scenario_results else 0,
        "average_scroll_length": round(mean(
            [r["metrics"].get("scroll_length", 0) for r in scenario_results if r["metrics"]]
        ), 2) if scenario_results else 0,
        "runtime_seconds": round(duration, 3),
    }
    results_path = project_root / "results" / "results_post.json"
    results_path.write_text(json.dumps({"scenarios": scenario_results, "summary": summary}, indent=2), encoding="utf-8")
    log_path = project_root / "logs" / "log_post.txt"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
