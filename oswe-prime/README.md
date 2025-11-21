# UI/UX Improvement Experiment

This workspace contains:
- Project_A_BaselineCourseUI
- Project_B_EnhancedCourseUI
- shared/test_scenarios.json

Run everything with one command:

```bash
./run_all.sh
```

Project setup (per project) example (bash/Git Bash):

```bash
pushd Project_A_BaselineCourseUI
./setup.sh
source .venv/bin/activate
./run_tests.sh
popd

pushd Project_B_EnhancedCourseUI
./setup.sh
source .venv/bin/activate
./run_tests.sh
popd
```

On Windows (PowerShell): create and activate a venv and run the project run_tests scripts.
