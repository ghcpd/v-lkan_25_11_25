#!/bin/bash

# KGEB Runtime Script
# Executes the complete KGEB pipeline with one command

set -e

echo "========================================"
echo "KGEB - Knowledge Graph Extraction"
echo "========================================"
echo ""

# Check if input file is provided
if [ $# -eq 0 ]; then
    INPUT_FILE="documents.txt"
    echo "No input file specified. Using default: $INPUT_FILE"
else
    INPUT_FILE=$1
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found"
    exit 1
fi

# Create timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "Input file: $INPUT_FILE"
echo "Timestamp: $TIMESTAMP"
echo ""

# Run tests first
echo "Step 1: Running tests..."
python tests/test_kgeb.py
if [ $? -eq 0 ]; then
    echo "✓ Tests passed"
else
    echo "✗ Tests failed"
    exit 1
fi

echo ""
echo "Step 2: Running extraction and evaluation pipeline..."
python src/pipeline.py "$INPUT_FILE" "KGEB-$TIMESTAMP"

echo ""
echo "========================================"
echo "Pipeline completed successfully!"
echo "========================================"
echo ""
echo "Output files:"
echo "  - output/entities_output.json"
echo "  - output/relations_output.json"
echo "  - output/evaluation_report.json"
echo ""
