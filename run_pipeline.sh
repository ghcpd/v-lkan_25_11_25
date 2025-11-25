#!/bin/bash
# KGEB Full Pipeline Runner
# Run the complete extraction and evaluation pipeline

set -e

echo "=========================================="
echo "KGEB Full Pipeline"
echo "=========================================="

# Default parameters
DOCUMENTS="documents.txt"
METHOD="KGEB Baseline Method"
OUTPUT_DIR="output"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --documents|-d)
            DOCUMENTS="$2"
            shift 2
            ;;
        --method|-m)
            METHOD="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./run_pipeline.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -d, --documents PATH    Path to documents file (default: documents.txt)"
            echo "  -m, --method NAME       Method name (default: KGEB Baseline Method)"
            echo "  -o, --output DIR        Output directory (default: output)"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if documents file exists
if [ ! -f "$DOCUMENTS" ]; then
    echo "❌ Error: Documents file not found: $DOCUMENTS"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"
mkdir -p logs

# Run pipeline
echo ""
echo "📋 Configuration:"
echo "   Documents: $DOCUMENTS"
echo "   Method: $METHOD"
echo "   Output: $OUTPUT_DIR"
echo ""

# Run with Python
python main.py run --documents "$DOCUMENTS" --method "$METHOD" --output-dir "$OUTPUT_DIR" | tee "logs/pipeline_$(date +%Y%m%d_%H%M%S).log"

# Check if pipeline succeeded
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo "✅ Pipeline completed successfully!"
    echo ""
    echo "📊 Results:"
    echo "   • Entities: $OUTPUT_DIR/entities_output.json"
    echo "   • Relations: $OUTPUT_DIR/relations_output.json"
    echo "   • Evaluation: $OUTPUT_DIR/evaluation_report.json"
else
    echo ""
    echo "❌ Pipeline failed!"
    exit 1
fi
