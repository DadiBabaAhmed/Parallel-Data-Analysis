#!/usr/bin/env bash
# Test Verification Script
# Run this to verify the test suite is working correctly

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Parallel Data Analysis Framework - Test Verification   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if pytest is installed
echo "→ Checking pytest installation..."
if ! python -m pytest --version &>/dev/null; then
    echo "✗ pytest not found. Installing pytest and dependencies..."
    pip install pytest pytest-cov
fi
echo "✓ pytest is available"
echo ""

# Navigate to Script directory
cd "$(dirname "$0")"
cd "Script" || {
    echo "✗ Cannot find Script directory"
    exit 1
}

echo "→ Checking test files..."
test_files=(
    "tests/conftest.py"
    "tests/test_data_loader.py"
    "tests/test_analyzer.py"
    "tests/test_graphs.py"
    "tests/test_api.py"
    "tests/test_main_smoke.py"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing!"
        exit 1
    fi
done
echo ""

echo "→ Checking documentation..."
docs=(
    "tests/README.md"
    "tests/QUICK_REFERENCE.md"
    "TESTING_STRATEGY.md"
    "pytest.ini"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "  ✓ $doc exists"
    else
        echo "  ✗ $doc missing!"
        exit 1
    fi
done
echo ""

echo "→ Running test discovery..."
test_count=$(python -m pytest tests/ --collect-only -q 2>/dev/null | tail -1 | grep -oE '[0-9]+' | head -1 || echo "0")
if [ "$test_count" -gt 0 ]; then
    echo "✓ Found $test_count tests"
else
    echo "✗ No tests found!"
    exit 1
fi
echo ""

echo "→ Running quick validation tests..."
echo "  Testing: DataLoader module..."
python -m pytest tests/test_data_loader.py::TestDataLoaderInitialization -q

echo "  Testing: DataAnalyzer module..."
python -m pytest tests/test_analyzer.py::TestDataAnalyzerInitialization -q

echo "  Testing: GraphGenerator module..."
python -m pytest tests/test_graphs.py::TestGraphGeneratorInitialization -q

echo "  Testing: Web API..."
python -m pytest tests/test_api.py::TestAPIInitialization -q

echo "  Testing: Main application..."
python -m pytest tests/test_main_smoke.py::TestParallelDataAnalysisInitialization -q

echo "✓ All quick validations passed"
echo ""

echo "→ Running full test suite..."
python -m pytest tests/ -v --tb=short

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✓ TEST VERIFICATION PASSED                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Run with coverage: pytest tests/ --cov=src --cov-report=html"
echo "  2. View coverage:     open htmlcov/index.html"
echo "  3. Read docs:         cat tests/README.md"
echo ""
