#!/bin/bash
# KGEB Quick Start Script
# Runs setup and executes the pipeline

echo "=========================================="
echo "KGEB Quick Start"
echo "=========================================="

# Run setup if not already done
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    bash setup.sh
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Run pipeline
echo ""
echo "Running KGEB pipeline..."
bash run_pipeline.sh

echo ""
echo "=========================================="
echo "Quick start complete!"
echo "=========================================="
