#!/bin/bash
# Run tests for Enhanced Course UI

echo "========================================="
echo "Running Enhanced Course UI Tests"
echo "========================================="

# Activate virtual environment if it exists
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Create results directory
mkdir -p results
mkdir -p logs

# Run tests
python tests/test_enhanced.py 2>&1 | tee logs/test_execution.log

# Check if tests ran successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Tests completed successfully"
    echo "Results available in: results/"
    echo "Logs available in: logs/"
else
    echo ""
    echo "✗ Tests encountered errors"
    exit 1
fi
