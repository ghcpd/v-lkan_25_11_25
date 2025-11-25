#!/bin/bash

# KGEB Setup Script
# Sets up the development environment for KGEB

set -e

echo "========================================"
echo "KGEB - Setup Environment"
echo "========================================"

# Check Python version
echo "[1/4] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated"
else
    echo "[2/4] Skipping virtual environment (use --venv flag to create one)"
fi

# Install dependencies
echo "[3/4] Installing dependencies..."
pip install -r requirements.txt
echo "Dependencies installed"

# Create necessary directories
echo "[4/4] Creating directories..."
mkdir -p data
mkdir -p output
mkdir -p logs
echo "Directories created"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the pipeline, use:"
echo "  python src/pipeline.py documents.txt"
echo ""
echo "To run tests, use:"
echo "  python tests/test_kgeb.py"
echo ""
