# Quick Start Guide

## Fastest Way to Run (Windows)

### Option 1: Run Everything (Recommended)
```cmd
run_all.bat
```

This will:
1. Run baseline tests (Project A)
2. Run enhanced tests (Project B)
3. Generate comparison report
4. Display summary

**Estimated Time:** 1-2 minutes

### Option 2: Run Tests Individually
```cmd
REM Baseline tests
cd Project_A_BaselineCourseUI
python tests\test_baseline.py

REM Enhanced tests
cd ..\Project_B_EnhancedCourseUI
python tests\test_enhanced.py

REM Generate report
cd ..
python generate_comparison_report.py
```

## What You'll Get

### 1. Test Results (JSON)
- `results/results_pre.json` - Baseline metrics
- `results/results_post.json` - Enhanced metrics

### 2. Visual Prototypes (HTML)
Open any of these in your browser:
- `results/scenario_01_normal_flow_enhanced_layout.html` ⭐ **Start here!**
- `results/scenario_02_mis_operation_flow_enhanced_layout.html`
- `results/scenario_03_long_scroll_flow_enhanced_layout.html`
- `results/scenario_04_complex_nesting_enhanced_layout.html`
- `results/scenario_05_malformed_input_enhanced_layout.html`

Compare with baseline versions:
- `results/scenario_01_normal_flow_baseline_layout.html`

### 3. Comparison Report
- `compare_report.md` - Full analysis with metrics

## Quick Verification

### Check if tests ran successfully:
```cmd
dir results
```

You should see:
- ✅ 10 HTML files (5 baseline + 5 enhanced)
- ✅ 2 JSON files (results_pre.json, results_post.json)
- ✅ 2 log files (log_pre.txt, log_post.txt)

### View comparison report:
```cmd
type compare_report.md | more
```

Or open in any markdown viewer/editor.

## Interactive Features in HTML Prototypes

### 1. Click Section Headers
Click "Syllabus", "Reviews", or "Related Courses" headers to expand/collapse.

### 2. Click CTA Button
Click "Enroll Now" to see confirmation modal (enhanced version only).

### 3. Click Attachments
Click attachment links to see preview simulation.

### 4. Resize Browser
Make browser window narrow to see mobile layout with bottom CTA bar.

## Key Metrics to Check

Open `results/results_post.json` and look for:

```json
"summary_metrics": {
  "avg_hierarchy_clarity_score": 0.87,  // Was 0.30 in baseline
  "avg_mis_operation_risk": 0.20,       // Was 1.00 in baseline
  "avg_scroll_reduction_percent": 28,    // Was 0% in baseline
  "collapsible_sections_avg": 2.4,       // Was 0 in baseline
  "pinned_elements_avg": 2.0             // Was 0 in baseline
}
```

## Expected Improvements

| Metric | Baseline | Enhanced | Change |
|--------|----------|----------|--------|
| Hierarchy | 0.30 | 0.87 | +190% |
| Risk | 1.00 | 0.20 | -80% |
| Scroll | 0% | 28% | +28pp |

## Troubleshooting

### Python not found?
```cmd
python --version
```
Should show Python 3.7+. If not, install Python from python.org.

### Tests not running?
```cmd
python -m pip install --upgrade pip
```
No external packages needed, but ensures pip is updated.

### No HTML output?
```cmd
mkdir results
cd Project_A_BaselineCourseUI
mkdir results
cd ..\Project_B_EnhancedCourseUI
mkdir results
cd ..
```

Then re-run tests.

## What Each Project Does

### Project A (Baseline) - The Problem
- ❌ Oversized hero (500-700px)
- ❌ All sections always expanded
- ❌ No pinned CTA
- ❌ Blocking fullscreen previews
- ❌ No confirmation prompts
- ❌ Public/internal content mixed

### Project B (Enhanced) - The Solution
- ✅ Reduced hero (300px, -40%)
- ✅ Collapsible sections (syllabus, reviews, related)
- ✅ Pinned info card + mobile CTA
- ✅ Non-blocking side-panel previews
- ✅ Two-step confirmation
- ✅ Content separation

## Next Steps

1. **View HTML prototypes** in browser for visual comparison
2. **Read compare_report.md** for detailed analysis
3. **Check results_post.json** for full metrics
4. **Review project READMEs** for implementation details

## Support

- **Project A Details:** `Project_A_BaselineCourseUI/README.md`
- **Project B Details:** `Project_B_EnhancedCourseUI/README.md`
- **Full Documentation:** `README.md`
- **Deliverables Summary:** `DELIVERABLES.md`

---

**Ready to start?** Just run: `run_all.bat`
