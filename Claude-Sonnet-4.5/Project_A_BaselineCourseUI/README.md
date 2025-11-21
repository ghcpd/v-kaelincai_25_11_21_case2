# Project A - Baseline Course UI

## Overview
This project implements a **baseline** (unoptimized) UI/UX transformation for an Online Course "Detail Page" scenario. It demonstrates the problematic state with:
- Oversized hero images
- No hierarchy optimization
- All sections always expanded
- Blocking fullscreen attachment previews
- No mis-operation prevention
- Public and internal content mixed together

## Structure
```
Project_A_BaselineCourseUI/
├── src/
│   └── baseline_ui.py          # Core transformation logic
├── tests/
│   └── test_baseline.py        # Automated test runner
├── results/                     # Test results and HTML prototypes
├── logs/                        # Execution logs
├── requirements.txt
├── setup.sh
├── run_tests.sh
└── README.md
```

## Setup

### Prerequisites
- Python 3.7 or higher

### Installation

#### Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

#### Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
mkdir results
mkdir logs
```

## Running Tests

### Linux/Mac:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Windows (PowerShell):
```powershell
venv\Scripts\activate
python tests\test_baseline.py
```

## Test Scenarios

The test suite evaluates 5 scenarios:

1. **scenario_01_normal_flow**: Standard course page with complete information
2. **scenario_02_mis_operation_flow**: Tests lack of enrollment confirmation (security issue)
3. **scenario_03_long_scroll_flow**: Overloaded content with poor scannability
4. **scenario_04_complex_nesting**: Deeply nested layout tree handling
5. **scenario_05_malformed_input**: Edge case with invalid data (expected to fail)

## Output

After running tests, you'll find:

- **results/results_pre.json**: Detailed test results in JSON format
- **results/log_pre.txt**: Human-readable test log
- **results/scenario_*_baseline_layout.html**: HTML prototypes for each scenario

## Known Issues (By Design)

These are **intentional limitations** of the baseline implementation:

### 1. Poor Information Hierarchy
- Hero image at full height (500-700px) pushes content below fold
- No pinned course info card
- Price and CTA only at bottom of page

### 2. Cognitive Overload
- All sections (syllabus, reviews, related courses) always expanded
- Full-width layout reduces scannability
- No visual segmentation or card-based design

### 3. Interaction Problems
- Attachment previews open in blocking fullscreen mode (context lost)
- No persistent CTA for mobile users
- Excessive scrolling required to reach enrollment

### 4. Security/Safety Issues
- **Public/Internal Content Mixed**: Author notes exposed in public description
- **No Mis-operation Prevention**: One-click enrollment without confirmation
- **No Price Warnings**: Expensive courses have no purchase safeguards

### 5. Poor Error Handling
- Crashes on malformed input (scenario_05)
- No XSS sanitization
- No safe fallbacks for missing fields

## Metrics (Baseline)

Expected baseline metrics:
- **Hierarchy Clarity Score**: ~0.3 (poor)
- **Mis-operation Risk**: 1.0 (maximum risk)
- **Scroll Optimization**: 0.0 (no optimization)
- **Edge Case Handling**: 0.2 (minimal)
- **Collapsible Sections**: 0 (none implemented)

## Interpreting Results

### Passing Tests
Tests are designed to **pass when baseline behaves as expected** (unoptimized). A passing test means:
- Info card is NOT pinned ✓
- Sections are NOT collapsible ✓
- Attachments use blocking preview ✓
- No enrollment confirmation ✓

### Failing Tests
scenario_05 (malformed input) is **expected to fail** in baseline, demonstrating lack of error handling.

## Usability Impact

This baseline demonstrates the following UX problems:

| Issue | Impact | User Frustration |
|-------|--------|------------------|
| Oversized hero | Key info below fold | High |
| No collapsible sections | Excessive scrolling | High |
| Bottom-only CTA | Hard to find on mobile | Medium |
| Blocking previews | Context loss | Medium |
| Mixed public/internal | Security risk | Critical |
| No confirmation | Accidental purchases | Critical |

## Next Steps

See **Project B (Enhanced Course UI)** for the optimized implementation that addresses all these issues.

## Limitations

- **Simulated Rendering**: No actual browser rendering; HTML prototypes for visual inspection only
- **Heuristic Metrics**: Clarity and risk scores are algorithmic estimates
- **Simplified Scoring**: Real-world usability testing would provide more accurate measures
