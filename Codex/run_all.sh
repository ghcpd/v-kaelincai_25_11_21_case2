#!/usr/bin/env bash
set -euo pipefail
find_python() {
  for candidate in python python3 py python.exe py.exe; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}
if ! PYTHON_BIN=$(find_python); then
  echo "Python interpreter not found." >&2
  exit 1
fi
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
pushd "$ROOT_DIR/Project_A_BaselineCourseUI" >/dev/null
./run_tests.sh
popd >/dev/null
pushd "$ROOT_DIR/Project_B_EnhancedCourseUI" >/dev/null
./run_tests.sh
popd >/dev/null
"${PYTHON_BIN}" "$ROOT_DIR/compare_results.py"
echo "All artifacts generated. See compare_report.md."