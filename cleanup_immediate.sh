#!/bin/bash
# Immediate Cleanup Script - ZERO RISK
# Removes only generated/temporary files (all regenerable)
# Run time: ~30 seconds
# Space saved: ~5.3MB

set -e

echo "============================================"
echo "AI Trading Bot - Immediate Cleanup"
echo "============================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to repository root
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo ""

# Function to calculate size
get_size() {
    if [ -d "$1" ] || [ -f "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1
    else
        echo "0"
    fi
}

# Track total savings
TOTAL_SAVED=0

echo "Phase 1: Python Cache Cleanup"
echo "------------------------------"
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
echo "Found: ${PYCACHE_COUNT} __pycache__ directories"
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✓ Removed all __pycache__ directories${NC}"
else
    echo "No __pycache__ directories found"
fi
echo ""

echo "Phase 2: HTML Coverage Reports"
echo "-------------------------------"
if [ -d "htmlcov" ]; then
    SIZE=$(get_size "htmlcov")
    rm -rf htmlcov/
    echo -e "${GREEN}✓ Removed htmlcov/ (${SIZE})${NC}"
else
    echo "No htmlcov/ directory found"
fi
echo ""

echo "Phase 3: Root Log Files"
echo "-----------------------"
LOG_COUNT=$(ls *.log 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    ls -lh *.log 2>/dev/null || true
    rm -f *.log
    echo -e "${GREEN}✓ Removed ${LOG_COUNT} log files${NC}"
else
    echo "No log files in root"
fi
echo ""

echo "Phase 4: Coverage Database"
echo "--------------------------"
if [ -f ".coverage" ]; then
    SIZE=$(get_size ".coverage")
    rm -f .coverage
    echo -e "${GREEN}✓ Removed .coverage (${SIZE})${NC}"
else
    echo "No .coverage file found"
fi
echo ""

echo "Phase 5: Backup Files"
echo "---------------------"
if [ -f ".env.backup" ]; then
    SIZE=$(get_size ".env.backup")
    rm -f .env.backup
    echo -e "${GREEN}✓ Removed .env.backup (${SIZE})${NC}"
else
    echo "No .env.backup file found"
fi
echo ""

echo "Phase 6: Windows Artifacts"
echo "--------------------------"
if [ -f "nul" ]; then
    rm -f nul
    echo -e "${GREEN}✓ Removed nul file${NC}"
else
    echo "No nul file found"
fi
echo ""

echo "Phase 7: Update .gitignore"
echo "--------------------------"
# Check if patterns already exist
MISSING_PATTERNS=0

if ! grep -q "^\*.backup$" .gitignore 2>/dev/null; then
    MISSING_PATTERNS=$((MISSING_PATTERNS + 1))
fi

if ! grep -q "^.env.backup$" .gitignore 2>/dev/null; then
    MISSING_PATTERNS=$((MISSING_PATTERNS + 1))
fi

if ! grep -q "^nul$" .gitignore 2>/dev/null; then
    MISSING_PATTERNS=$((MISSING_PATTERNS + 1))
fi

if [ "$MISSING_PATTERNS" -gt 0 ]; then
    echo "Adding missing patterns to .gitignore..."
    cat >> .gitignore << 'EOF'

# Additional cleanup patterns (added by cleanup_immediate.sh)
*.backup
.env.backup
nul
Thumbs.db
/*.log
.coverage.*
coverage.xml
EOF
    echo -e "${GREEN}✓ Updated .gitignore with ${MISSING_PATTERNS} new patterns${NC}"
else
    echo "All cleanup patterns already in .gitignore"
fi
echo ""

echo "============================================"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo "============================================"
echo ""
echo "Summary:"
echo "  - Python cache removed"
echo "  - HTML coverage removed"
echo "  - Root log files removed"
echo "  - Coverage database removed"
echo "  - Backup files removed"
echo "  - .gitignore updated"
echo ""
echo "Next steps:"
echo "  1. Run tests: python -m pytest tests/ -v"
echo "  2. Verify no issues: git status"
echo "  3. Review full report: cat REPOSITORY_CLEANUP_REPORT.md"
echo ""
echo "For more comprehensive cleanup, see Phase 2-6 in:"
echo "  REPOSITORY_CLEANUP_REPORT.md"
echo ""
