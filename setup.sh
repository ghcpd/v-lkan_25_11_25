#!/bin/bash
# Enterprise Knowledge Graph Extraction Benchmark (KGEB)
# Setup script for reproducible environment

set -e

echo "=========================================="
echo "KGEB Setup Script"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python --version

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Create output directories
echo "Creating output directories..."
mkdir -p output
mkdir -p logs
mkdir -p test_results

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate   (Linux/Mac)"
echo "  venv\\Scripts\\activate      (Windows)"
echo ""
echo "To run the benchmark, use:"
echo "  python main.py --help"
