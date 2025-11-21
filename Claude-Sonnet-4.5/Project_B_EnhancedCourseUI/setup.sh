#!/bin/bash
# Setup script for Enhanced Course UI project

echo "========================================="
echo "Setting up Enhanced Course UI Environment"
echo "========================================="

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install dependencies
pip install --upgrade pip

# Create necessary directories
mkdir -p results
mkdir -p logs

echo "✓ Setup complete!"
echo "To activate environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
