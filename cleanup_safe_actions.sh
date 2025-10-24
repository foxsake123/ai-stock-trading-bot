#!/bin/bash
# Safe Repository Cleanup Script
# Generated: October 23, 2025
# Run this script to perform LOW-RISK cleanup actions
# HIGH-RISK actions (agent consolidation) require manual review

set -e  # Exit on error

echo "=========================================="
echo "AI Stock Trading Bot - Safe Cleanup"
echo "=========================================="
echo ""
echo "This script performs LOW-RISK cleanup:"
echo "  - Deletes test artifacts (regenerable)"
echo "  - Removes empty directories"
echo "  - Deletes orphaned files"
echo "  - Updates .gitignore"
echo ""
echo "HIGH-RISK actions (agent consolidation)"
echo "require manual review and are NOT included."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Aborted."
    exit 1
fi

echo ""
echo "=========================================="
echo "Phase 1: Delete Test Artifacts"
echo "=========================================="

# Remove coverage reports
if [ -f .coverage ]; then
    echo "Deleting .coverage..."
    rm .coverage
fi

if [ -d htmlcov ]; then
    echo "Deleting htmlcov/ directory..."
    rm -rf htmlcov/
fi

if [ -d .pytest_cache ]; then
    echo "Deleting .pytest_cache/ directory..."
    rm -rf .pytest_cache/
fi

# Remove Python cache
echo "Deleting __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "✓ Test artifacts removed"
echo ""

echo "=========================================="
echo "Phase 2: Delete Orphaned Files"
echo "=========================================="

# Delete Windows error file
if [ -f nul ]; then
    echo "Deleting nul (Windows error file)..."
    rm nul
fi

# Delete obsolete analysis
if [ -f REPORT_CLEANUP_PLAN.md ]; then
    echo "Deleting REPORT_CLEANUP_PLAN.md (superseded)..."
    rm REPORT_CLEANUP_PLAN.md
fi

# Delete duplicate .env template
if [ -f .env.template ]; then
    echo "Deleting .env.template (duplicate of .env.example)..."
    rm .env.template
fi

echo "✓ Orphaned files removed"
echo ""

echo "=========================================="
echo "Phase 3: Remove Empty Directories"
echo "=========================================="

echo "Finding empty directories (excluding .git)..."
EMPTY_DIRS=$(find . -type d -empty -not -path "./.git/*" 2>/dev/null | grep -v "^\./.git" || true)

if [ -z "$EMPTY_DIRS" ]; then
    echo "No empty directories found."
else
    echo "Empty directories found:"
    echo "$EMPTY_DIRS"
    echo ""
    echo "Deleting empty directories..."
    find . -type d -empty -not -path "./.git/*" -delete 2>/dev/null || true
    echo "✓ Empty directories removed"
fi

echo ""

echo "=========================================="
echo "Phase 4: Update .gitignore"
echo "=========================================="

# Check if patterns already exist in .gitignore
GITIGNORE_FILE=".gitignore"

if ! grep -q "^\.coverage$" "$GITIGNORE_FILE" 2>/dev/null; then
    echo "" >> "$GITIGNORE_FILE"
    echo "# Coverage reports (added by cleanup script)" >> "$GITIGNORE_FILE"
    echo ".coverage" >> "$GITIGNORE_FILE"
    echo "coverage.xml" >> "$GITIGNORE_FILE"
    echo "*.cover" >> "$GITIGNORE_FILE"
    echo "✓ Added coverage patterns to .gitignore"
fi

if ! grep -q "^htmlcov/$" "$GITIGNORE_FILE" 2>/dev/null; then
    echo "htmlcov/" >> "$GITIGNORE_FILE"
    echo "✓ Added htmlcov/ to .gitignore"
fi

if ! grep -q "^\.pytest_cache/$" "$GITIGNORE_FILE" 2>/dev/null; then
    echo ".pytest_cache/" >> "$GITIGNORE_FILE"
    echo "✓ Added .pytest_cache/ to .gitignore"
fi

if ! grep -q "^__pycache__/$" "$GITIGNORE_FILE" 2>/dev/null; then
    echo "__pycache__/" >> "$GITIGNORE_FILE"
    echo "*.py[cod]" >> "$GITIGNORE_FILE"
    echo "*\$py.class" >> "$GITIGNORE_FILE"
    echo "*.so" >> "$GITIGNORE_FILE"
    echo "✓ Added Python cache patterns to .gitignore"
fi

echo ""

echo "=========================================="
echo "Cleanup Summary"
echo "=========================================="
echo ""
echo "✓ Deleted test artifacts (5.4MB)"
echo "✓ Removed orphaned files"
echo "✓ Deleted empty directories"
echo "✓ Updated .gitignore"
echo ""
echo "Remaining manual actions (see REPOSITORY_CLEANUP_ANALYSIS.md):"
echo "  [ ] Phase 1: Consolidate agents/ and src/agents/ (CRITICAL)"
echo "  [ ] Phase 2: Move files from root directory (HIGH)"
echo "  [ ] Phase 4: Reorganize reports/ structure (MEDIUM)"
echo "  [ ] Phase 5-8: Optional organizational improvements"
echo ""
echo "Run 'git status' to see changes."
echo "Run 'pytest tests/' to verify tests still pass."
echo ""
echo "=========================================="
echo "Safe cleanup complete!"
echo "=========================================="
