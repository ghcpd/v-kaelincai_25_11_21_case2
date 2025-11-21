@echo off
echo Running Project A (baseline)
cd /d %~dp0\Project_A_BaselineCourseUI
call run_tests.sh
echo Running Project B (enhanced)
cd /d %~dp0\Project_B_EnhancedCourseUI
call run_tests.sh
cd /d %~dp0
python aggregate_results.py
echo Done. See compare_report.md
