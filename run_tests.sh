#!/bin/bash
# AI Trading Bot - Test Runner Script
# Runs comprehensive test suite with coverage reporting

set -e  # Exit on error

echo "================================================================================"
echo "AI TRADING BOT - TEST SUITE"
echo "================================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-cov pytest-mock"
    exit 1
fi

echo -e "${YELLOW}Step 1: Running Unit Tests${NC}"
echo "--------------------------------------------------------------------------------"
pytest tests/test_*.py -v -m "not integration" --tb=short || true
echo ""

echo -e "${YELLOW}Step 2: Running Integration Tests${NC}"
echo "--------------------------------------------------------------------------------"
pytest tests/test_integration.py -v -m integration --tb=short || true
echo ""

echo -e "${YELLOW}Step 3: Running All Tests with Coverage${NC}"
echo "--------------------------------------------------------------------------------"
pytest tests/ -v \
    --cov=. \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-config=.coveragerc \
    --tb=short \
    || true
echo ""

echo "================================================================================"
echo -e "${GREEN}TEST SUITE COMPLETE${NC}"
echo "================================================================================"
echo ""
echo "Coverage Report:"
echo "  - HTML: htmlcov/index.html"
echo "  - Open with: open htmlcov/index.html (Mac) or xdg-open htmlcov/index.html (Linux)"
echo ""
echo "Test Summary:"
pytest tests/ --collect-only -q 2>/dev/null | tail -n 1 || echo "  See output above"
echo ""
echo "Next Steps:"
echo "  1. Review coverage report in htmlcov/index.html"
echo "  2. Fix any failing tests"
echo "  3. Aim for >50% coverage on new code"
echo ""
echo "================================================================================"
