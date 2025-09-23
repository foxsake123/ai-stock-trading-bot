#!/bin/bash
# Bash Undo Script for AI Trading Bot Reorganization
# Standalone undo mechanism with safeguards

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check for force flag
FORCE=false
if [ "$1" == "--force" ]; then
    FORCE=true
fi

# Find the most recent reorg log
LATEST_LOG=$(ls -t reorg-*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo -e "${RED}ERROR: No reorganization log found. Nothing to undo.${NC}"
    exit 1
fi

echo -e "${YELLOW}Found reorganization log: $LATEST_LOG${NC}"

# Confirmation prompt
if [ "$FORCE" != "true" ]; then
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}REORGANIZATION UNDO UTILITY${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo -e "${YELLOW}This will reverse the reorganization performed on:${NC}"
    echo -e "${YELLOW}  Log file: $LATEST_LOG${NC}"
    echo -e "${YELLOW}  Date: $(stat -c %y "$LATEST_LOG" 2>/dev/null || stat -f "%Sm" "$LATEST_LOG")${NC}"
    echo -e "\nThis operation will:"
    echo "  1. Move all files back to their original locations"
    echo "  2. Recreate original directory structure"
    echo "  3. Remove new directories if empty"
    echo -e "\n${RED}Are you sure you want to continue? (Y/N): ${NC}"
    read -r confirmation

    if [ "$confirmation" != "Y" ] && [ "$confirmation" != "y" ]; then
        echo -e "${GREEN}Undo cancelled by user.${NC}"
        exit 0
    fi
fi

# Create undo log
UNDO_LOG="undo-$(date +%Y%m%d-%H%M%S).log"
echo "Undo operation started: $(date)" > "$UNDO_LOG"
echo "Reversing changes from: $LATEST_LOG" >> "$UNDO_LOG"

# Parse log file and extract moves
MOVES_FILE=$(mktemp)
DUPLICATES_FILE=$(mktemp)

# Extract successful moves
grep "\[SUCCESS\] MOVED:" "$LATEST_LOG" | sed -n 's/.*MOVED: \(.*\) -> \(.*\) |.*/\1|\2/p' > "$MOVES_FILE"

# Extract duplicates
grep "\[WARNING\] DUPLICATE:" "$LATEST_LOG" | sed -n 's/.*DUPLICATE: \(.*\) -> \(.*\) (identical.*/\1|\2/p' > "$DUPLICATES_FILE"

MOVE_COUNT=$(wc -l < "$MOVES_FILE")
DUP_COUNT=$(wc -l < "$DUPLICATES_FILE")

echo -e "\n${YELLOW}Found $MOVE_COUNT file moves to undo${NC}"
echo -e "${YELLOW}Found $DUP_COUNT duplicates to restore${NC}"

# Reverse moves (process in reverse order)
SUCCESS_COUNT=0
ERROR_COUNT=0

# Use tac (reverse cat) to process moves in reverse order
tac "$MOVES_FILE" | while IFS='|' read -r original_location current_location; do
    # Trim whitespace
    original_location=$(echo "$original_location" | xargs)
    current_location=$(echo "$current_location" | xargs)

    if [ -e "$current_location" ]; then
        # Create original directory if needed
        orig_dir=$(dirname "$original_location")
        mkdir -p "$orig_dir"

        # Move file back
        if mv "$current_location" "$original_location" 2>/dev/null; then
            echo -e "${GREEN}✓ Restored: $original_location${NC}"
            echo "RESTORED: $current_location -> $original_location" >> "$UNDO_LOG"
            ((SUCCESS_COUNT++))
        else
            echo -e "${RED}✗ Failed to restore: $original_location${NC}"
            echo "ERROR: Failed to restore $original_location" >> "$UNDO_LOG"
            ((ERROR_COUNT++))
        fi
    else
        echo -e "${YELLOW}⚠ File not found at: $current_location${NC}"
        echo "WARNING: File not found at $current_location" >> "$UNDO_LOG"
    fi
done

# Restore duplicates
while IFS='|' read -r original_location archive_location; do
    # Trim whitespace
    original_location=$(echo "$original_location" | xargs)
    archive_location=$(echo "$archive_location" | xargs)

    if [ -e "$archive_location" ]; then
        # Create original directory if needed
        orig_dir=$(dirname "$original_location")
        mkdir -p "$orig_dir"

        # Restore duplicate
        if mv "$archive_location" "$original_location" 2>/dev/null; then
            echo -e "${GREEN}✓ Restored duplicate: $original_location${NC}"
            echo "RESTORED DUPLICATE: $archive_location -> $original_location" >> "$UNDO_LOG"

            # Remove pointer file if exists
            [ -f "${archive_location}.pointer" ] && rm -f "${archive_location}.pointer"
        else
            echo -e "${RED}✗ Failed to restore duplicate: $original_location${NC}"
            echo "ERROR: Failed to restore duplicate $original_location" >> "$UNDO_LOG"
        fi
    fi
done < "$DUPLICATES_FILE"

# Clean up temp files
rm -f "$MOVES_FILE" "$DUPLICATES_FILE"

# Clean up empty directories created during reorganization
echo -e "\n${YELLOW}Cleaning up empty directories...${NC}"
DIRS_TO_CHECK=(
    "agents/core" "agents/dee-bot" "agents/shorgan-bot" "agents/communication"
    "agents/execution" "agents/legacy" "scripts-and-data/data"
    "research" "utils/extensions" "logs/trading" "_archive/duplicates"
)

for dir in "${DIRS_TO_CHECK[@]}"; do
    if [ -d "$dir" ] && [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
        rmdir "$dir" 2>/dev/null && echo -e "  ${GRAY}Removed empty directory: $dir${NC}"
    fi
done

# Count final statistics
FINAL_SUCCESS=$(grep -c "^RESTORED:" "$UNDO_LOG" || true)
FINAL_ERRORS=$(grep -c "^ERROR:" "$UNDO_LOG" || true)

# Summary
echo -e "\n${CYAN}========================================${NC}"
echo -e "${CYAN}UNDO OPERATION COMPLETE${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Files restored: $FINAL_SUCCESS${NC}"
if [ "$FINAL_ERRORS" -gt 0 ]; then
    echo -e "${RED}Errors: $FINAL_ERRORS${NC}"
else
    echo -e "${GREEN}Errors: 0${NC}"
fi
echo -e "${YELLOW}Undo log: $UNDO_LOG${NC}"

echo "Undo operation completed: $(date)" >> "$UNDO_LOG"
echo "Files restored: $FINAL_SUCCESS" >> "$UNDO_LOG"
echo "Errors: $FINAL_ERRORS" >> "$UNDO_LOG"

# Verify main.py is back
if [ -f "main.py" ]; then
    echo -e "\n${GREEN}✓ main.py is present${NC}"
else
    echo -e "\n${RED}⚠ WARNING: main.py not found in root${NC}"
fi

echo -e "\n${GREEN}Repository structure has been restored to original state.${NC}"
echo -e "${YELLOW}Run 'git status' to verify changes.${NC}"