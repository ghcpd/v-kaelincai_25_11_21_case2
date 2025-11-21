import json
import sys
import traceback
from pathlib import Path

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from transformer import transform_layout  # type: ignore
from metrics import compute_metrics  # type: ignore
from html_generator import generate_html  # type: ignore


def evaluate_thresholds(metrics, thresholds):
    passed = True
    messages = []
    for name, opts in (thresholds or {}).items():
        if name not in metrics:
            continue
        val = metrics[name]
        if isinstance(opts, dict):
            if "baseline_max" in opts and val > opts["baseline_max"]:
                passed = False
                messages.append(f"{name}={val} > baseline_max={opts['baseline_max']}")
            if "baseline_min" in opts and val < opts["baseline_min"]:
                passed = False
                messages.append(f"{name}={val} < baseline_min={opts['baseline_min']}")
    return passed, messages


def main(scenarios_path: Path):
    results = []
    log_lines = []
    html_generated = False
    for scenario in json.loads(scenarios_path.read_text(encoding="utf-8")):
        sid = scenario.get("id")
        log_lines.append(f"Scenario: {sid}")
        try:
            transformed = transform_layout(scenario.get("input_layout"))
            metrics = compute_metrics(transformed)
            status = "warning" if transformed.get("warnings") else "ok"
            thresholds = scenario.get("thresholds", {})
            passed, msgs = evaluate_thresholds(metrics, thresholds)
            # Compare status
            expected_status = scenario.get("expected", {}).get("status")
            if expected_status and expected_status != status:
                passed = False
                msgs.append(f"status mismatch: got {status}, expected {expected_status}")
            result = {
                "scenario_id": sid,
                "passed": passed,
                "status": status,
                "metrics": metrics,
                "warnings": transformed.get("warnings", []),
                "edge_case_flags": transformed.get("edge_case_flags", []),
                "messages": msgs,
                "metadata": transformed.get("metadata", {}),
            }
            results.append(result)
            log_lines.append(f"  status={status} passed={passed} metrics={metrics} msgs={msgs}")
            # Generate one prototype HTML for inspection (first scenario)
            if not html_generated:
                out_html = ROOT / "baseline_layout.html"
                generate_html(transformed.get("layout", {}), out_html)
                # also copy to results for traceability
                (ROOT / "results").mkdir(parents=True, exist_ok=True)
                generate_html(transformed.get("layout", {}), ROOT / "results" / "baseline_layout.html")
                log_lines.append(f"  HTML prototype generated at {out_html}")
                html_generated = True
        except Exception as e:
            tb = traceback.format_exc()
            log_lines.append(f"  ERROR: {e}\n{tb}")
            results.append({
                "scenario_id": sid,
                "passed": False,
                "status": "error",
                "metrics": {},
                "warnings": ["exception"],
                "edge_case_flags": [],
                "messages": [str(e)],
            })
    # Write results
    results_path = ROOT / "results" / "results_pre.json"
    logs_path = ROOT / "logs" / "log_pre.txt"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logs_path.write_text("\n".join(log_lines), encoding="utf-8")

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    print(f"Baseline: {passed}/{total} scenarios passed")

if __name__ == "__main__":
    scenarios_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "test_scenarios.json"
    main(scenarios_path)
