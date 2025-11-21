#!/usr/bin/env python3
"""Runs baseline scenarios and captures metrics/logs for comparison."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from layout_transformer import CourseLayoutTransformer  # type: ignore  # noqa: E402


class BaselineValidator:
    def validate(self, layout_result, scenario: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        layout = layout_result.layout
        metrics = layout_result.metrics
        expectations = scenario.get("expectations", {})
        required_fields = expectations.get("output_fields", [])
        for field in required_fields:
            if not hasattr(layout_result, field) and field not in {"metrics", "ui_warnings", "edge_case_flags", "errors"}:
                errors.append(f"Missing required field: {field}")
        for metric in expectations.get("required_metrics", []):
            if metric == "errors":
                if not layout_result.errors:
                    errors.append("Missing metric: errors")
                continue
            if metric not in metrics:
                errors.append(f"Missing metric: {metric}")
        if layout.get("collapsible_sections"):
            errors.append("Baseline should not enable collapsible sections")
        if layout.get("cta", {}).get("persistent"):
            errors.append("Baseline CTA should not be persistent")
        preview_mode = layout.get("attachment_preview", {}).get("mode")
        if preview_mode != "overlay":
            errors.append("Baseline preview must block context")
        hierarchy_target = 65 if scenario["id"] == "mis_operation_flow" else 55
        if metrics.get("mis_operation_risk", 0) < hierarchy_target:
            warnings.append("Mis-operation risk unexpectedly low for baseline")
        status = "passed" if not errors else "failed"
        return {"status": status, "errors": errors, "warnings": warnings}


def load_scenarios() -> List[Dict[str, Any]]:
    scenario_path = Path(__file__).resolve().parents[2] / "test_scenarios.json"
    with scenario_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    prototype_dir = project_root / "prototypes"
    transformer = CourseLayoutTransformer(prototype_dir=prototype_dir)
    scenarios = load_scenarios()
    validator = BaselineValidator()
    scenario_results: List[Dict[str, Any]] = []
    log_lines: List[str] = []
    failures = 0
    start = time.time()
    for scenario in scenarios:
        try:
            layout_result = transformer.transform(scenario)
            validation = validator.validate(layout_result, scenario)
            combined_errors = list(layout_result.errors)
            result_entry = {
                "id": scenario["id"],
                "status": layout_result.status if validation["status"] == "passed" else "failed",
                "metrics": layout_result.metrics,
                "ui_warnings": layout_result.ui_warnings,
                "edge_case_flags": layout_result.edge_case_flags,
                "errors": combined_errors + validation["errors"],
                "prototype_path": layout_result.prototype_path,
            }
            if validation["errors"]:
                failures += 1
            if validation["warnings"]:
                result_entry.setdefault("ui_warnings", []).extend(validation["warnings"])
            scenario_results.append(result_entry)
            log_lines.append(
                f"[{scenario['id']}] status={result_entry['status']} "
                f"hierarchy={layout_result.metrics.get('hierarchy_clarity')} "
                f"scroll={layout_result.metrics.get('scroll_length')}"
            )
        except Exception as exc:  # pragma: no cover - defensive
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
    results_payload = {"scenarios": scenario_results, "summary": summary}
    results_path = project_root / "results" / "results_pre.json"
    results_path.write_text(json.dumps(results_payload, indent=2), encoding="utf-8")
    log_path = project_root / "logs" / "log_pre.txt"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
