@echo off
REM Master script to run both projects and generate comparison report (Windows)

echo ================================================================================
echo ONLINE COURSE UI/UX IMPROVEMENT - COMPREHENSIVE TEST SUITE
echo ================================================================================
echo.

REM Create results directory
if not exist results mkdir results

REM Run Project A (Baseline)
echo ================================================================================
echo PHASE 1: Running Baseline Course UI Tests
echo ================================================================================
cd Project_A_BaselineCourseUI

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
)

if not exist results mkdir results
if not exist logs mkdir logs

python tests\test_baseline.py

cd ..

REM Copy baseline results
xcopy /Y /E Project_A_BaselineCourseUI\results\* results\ 2>nul

echo.
echo ================================================================================
echo PHASE 2: Running Enhanced Course UI Tests
echo ================================================================================
cd Project_B_EnhancedCourseUI

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
)

if not exist results mkdir results
if not exist logs mkdir logs

python tests\test_enhanced.py

cd ..

REM Copy enhanced results
xcopy /Y /E Project_B_EnhancedCourseUI\results\* results\ 2>nul

echo.
echo ================================================================================
echo PHASE 3: Generating Comparison Report
echo ================================================================================

REM Generate comparison report using Python
python -c "import json; import os; from datetime import datetime; exec(open('generate_report.py').read())" 2>nul

if not exist generate_report.py (
    echo Creating report generator...
    python generate_comparison_report.py
)

echo.
echo ================================================================================
echo ALL TESTS COMPLETE
echo ================================================================================
echo.
echo Summary:
echo   - Baseline results: results\results_pre.json
echo   - Enhanced results: results\results_post.json
echo   - Comparison report: compare_report.md
echo   - HTML prototypes: results\*.html
echo.
echo Check compare_report.md for detailed analysis
echo Open HTML prototypes in browser for visual inspection
echo.

pause
