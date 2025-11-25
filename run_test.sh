#!/bin/bash
# KGEB Test Runner Script
# One-click script to run all tests

set -e

echo "=========================================="
echo "KGEB Test Suite Runner"
echo "=========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source venv/bin/activate (or venv\\Scripts\\activate on Windows)"
    exit 1
fi

# Create test results directory
mkdir -p test_results

# Run tests with coverage
echo ""
echo "🧪 Running tests with coverage..."
pytest test_kgeb.py -v --cov=. --cov-report=html --cov-report=term --cov-report=json \
    --junitxml=test_results/junit.xml \
    --html=test_results/report.html --self-contained-html

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Test reports generated:"
    echo "   • HTML Report: test_results/report.html"
    echo "   • Coverage Report: htmlcov/index.html"
    echo "   • JUnit XML: test_results/junit.xml"
    echo "   • Coverage JSON: coverage.json"
else
    echo ""
    echo "❌ Tests failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Test run complete!"
echo "=========================================="
