import json
from pathlib import Path

def load_results(path):
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def build_report(baseline, enhanced):
    # Index by scenario
    bmap = {r.get("scenario_id"): r for r in baseline}
    emap = {r.get("scenario_id"): r for r in enhanced}
    scenarios = sorted(set(bmap.keys()) | set(emap.keys()))

    lines = []
    lines.append("# Compare Report")
    lines.append("")
    lines.append("## Pass/Fail Matrix")
    lines.append("| Scenario | Baseline | Enhanced |")
    lines.append("|---|---|---|")
    for sid in scenarios:
        b = bmap.get(sid, {})
        e = emap.get(sid, {})
        lines.append(f"| {sid} | {'✅' if b.get('passed') else '❌'} | {'✅' if e.get('passed') else '❌'} |")

    lines.append("")
    lines.append("## Metrics Comparison")
    lines.append("| Scenario | Clarity Δ (enh-bas) | Scroll Δ (bas-enh) | Mis-op Risk Δ (bas-enh) | Edge Coverage Δ |")
    lines.append("|---|---|---|---|---|")
    for sid in scenarios:
        b = bmap.get(sid, {})
        e = emap.get(sid, {})
        bm = b.get("metrics", {}) if b else {}
        em = e.get("metrics", {}) if e else {}
        clarity_delta = (em.get("hierarchy_clarity") or 0) - (bm.get("hierarchy_clarity") or 0)
        scroll_delta = (bm.get("scroll_length") or 0) - (em.get("scroll_length") or 0)
        misop_delta = (bm.get("misop_risk") or 0) - (em.get("misop_risk") or 0)
        edge_delta = (em.get("edge_coverage") or 0) - (bm.get("edge_coverage") or 0)
        lines.append(f"| {sid} | {clarity_delta:.2f} | {scroll_delta:.0f} | {misop_delta:.2f} | {edge_delta:.2f} |")

    lines.append("")
    lines.append("## Observations")
    lines.append("- **Hierarchy clarity** improves if Δ > 0 (positive values indicate enhancement).")
    lines.append("- **Scroll Δ** represents estimated reduction (positive values indicate fewer pixels/points).")
    lines.append("- **Mis-operation risk Δ** positive values indicate reduced risk.")
    lines.append("- **Edge coverage** increases with better handling of malformed/unsafe inputs.")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("- Baseline prototype: `Project_A_BaselineCourseUI/baseline_layout.html`\n- Enhanced prototype: `Project_B_EnhancedCourseUI/enhanced_layout.html`")

    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parent
    baseline_path = root / "Project_A_BaselineCourseUI" / "results" / "results_pre.json"
    enhanced_path = root / "Project_B_EnhancedCourseUI" / "results" / "results_post.json"
    baseline = load_results(baseline_path)
    enhanced = load_results(enhanced_path)
    report_md = build_report(baseline, enhanced)
    (root / "compare_report.md").write_text(report_md, encoding="utf-8")
    # aggregate json
    combined = {"baseline": baseline, "enhanced": enhanced}
    (root / "results").mkdir(exist_ok=True)
    (root / "results" / "combined_results.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print("Compare report generated at compare_report.md")

if __name__ == "__main__":
    main()
