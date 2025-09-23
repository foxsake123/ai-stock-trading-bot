#!/bin/bash
# Bash Reorganization Script for AI Trading Bot
# Target: LuckyOne7777 ChatGPT-Micro-Cap-Experiment structure
# Date: September 23, 2025

set -e

# Default mode
MODE="${1:---dry-run}"
REORG_LOG="reorg-$(date +%Y%m%d-%H%M%S).log"
MAPPING_FILE="mapping-complete.csv"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
write_log() {
    local message="$1"
    local type="${2:-INFO}"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local log_entry="$timestamp [$type] $message"

    echo "$log_entry" >> "$REORG_LOG"

    case "$type" in
        ERROR) echo -e "${RED}$log_entry${NC}" ;;
        SUCCESS) echo -e "${GREEN}$log_entry${NC}" ;;
        WARNING) echo -e "${YELLOW}$log_entry${NC}" ;;
        *) echo "$log_entry" ;;
    esac
}

# Create directory structure
initialize_directories() {
    local directories=(
        "agents/core"
        "agents/dee-bot/strategies"
        "agents/dee-bot/analysis"
        "agents/shorgan-bot/strategies"
        "agents/shorgan-bot/analysis"
        "agents/communication"
        "agents/execution"
        "agents/legacy"
        "scripts-and-data/automation"
        "scripts-and-data/scripts/setup"
        "scripts-and-data/data/positions"
        "scripts-and-data/data/performance"
        "scripts-and-data/data/reports/daily"
        "scripts-and-data/data/reports/weekly"
        "scripts-and-data/data/reports/post-market"
        "scripts-and-data/data/market"
        "scripts-and-data/data/portfolio"
        "scripts-and-data/data/metrics"
        "scripts-and-data/data/json"
        "scripts-and-data/data/db"
        "scripts-and-data/utilities"
        "research/pdf"
        "research/md"
        "research/chatgpt"
        "research/multi-agent"
        "research/reports/pre-market"
        "research/data"
        "docs/guides"
        "docs/session-logs"
        "docs/daily-orders"
        "docs/reports"
        "docs/index"
        "docs/legacy"
        "configs/bots"
        "configs/claude"
        "frontend/legacy"
        "backtests/strategies"
        "backtests/results"
        "risk/models"
        "risk/reports"
        "utils/tests"
        "utils/tools"
        "utils/extensions/chatgpt"
        "utils/legacy"
        "logs/trading/dee"
        "logs/trading/shorgan"
        "logs/system"
        "logs/snapshots"
        "logs/automation"
        "_archive/deprecated"
        "_archive/duplicates"
        "_archive/legacy"
        "_archive/misc"
        "_archive/temp/pytest-cache"
        "_archive/temp/pycache"
        "_archive/logs"
        "_archive/legacy_structure"
    )

    for dir in "${directories[@]}"; do
        if [ "$MODE" == "--apply" ]; then
            mkdir -p "$dir"
            write_log "Created directory: $dir" "SUCCESS"
        else
            write_log "Would create directory: $dir" "INFO"
        fi
    done
}

# Calculate SHA-256 hash
get_file_hash() {
    local file="$1"
    if [ -f "$file" ]; then
        if command -v sha256sum >/dev/null 2>&1; then
            sha256sum "$file" | cut -d' ' -f1
        elif command -v shasum >/dev/null 2>&1; then
            shasum -a 256 "$file" | cut -d' ' -f1
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# Convert to kebab-case
to_kebab_case() {
    local input="$1"
    echo "$input" | sed 's/_/-/g' | sed 's/\([A-Z]\)/-\1/g' | sed 's/^-//' | sed 's/--/-/g' | tr '[:upper:]' '[:lower:]'
}

# Move file with logging
move_file_with_log() {
    local source="$1"
    local destination="$2"
    local reason="$3"

    if [ ! -e "$source" ]; then
        write_log "Source not found: $source" "WARNING"
        return
    fi

    local dest_dir=$(dirname "$destination")

    if [ "$MODE" == "--apply" ]; then
        # Create destination directory if needed
        mkdir -p "$dest_dir"

        # Check for duplicates
        if [ -f "$destination" ]; then
            local source_hash=$(get_file_hash "$source")
            local dest_hash=$(get_file_hash "$destination")

            if [ "$source_hash" == "$dest_hash" ] && [ -n "$source_hash" ]; then
                # Files are identical, archive the source
                local dup_dest="_archive/duplicates/$(basename "$source")"
                mv "$source" "$dup_dest"
                write_log "DUPLICATE: $source -> $dup_dest (identical to $destination)" "WARNING"
                # Create pointer file
                echo "Original location: $destination" > "${dup_dest}.pointer"
                return
            else
                # Files differ, rename destination
                local timestamp=$(date +%Y%m%d-%H%M%S)
                local new_dest="${destination}.${timestamp}"
                mv "$source" "$new_dest"
                write_log "MOVED: $source -> $new_dest (collision resolved)" "SUCCESS"
                return
            fi
        fi

        mv "$source" "$destination"
        write_log "MOVED: $source -> $destination | Reason: $reason" "SUCCESS"
    else
        write_log "DRY-RUN: Would move $source -> $destination | Reason: $reason" "INFO"
    fi
}

# Process mapping file
process_mapping() {
    if [ ! -f "$MAPPING_FILE" ]; then
        write_log "Mapping file not found: $MAPPING_FILE" "ERROR"
        exit 1
    fi

    local total_moves=$(grep -v '^#' "$MAPPING_FILE" | wc -l)
    local current_move=0

    while IFS=',' read -r source_path dest_path reason; do
        # Skip comments and empty lines
        if [[ "$source_path" == \#* ]] || [ -z "$source_path" ]; then
            continue
        fi

        ((current_move++))
        echo -ne "Processing files: $current_move of $total_moves\r"

        # Handle wildcards
        if [[ "$source_path" == *"*"* ]]; then
            for file in $source_path; do
                if [ -e "$file" ]; then
                    local dest="$dest_path"
                    if [[ "$dest" == */ ]]; then
                        dest="${dest}$(basename "$file")"
                    fi
                    # Convert to kebab-case
                    local dest_name=$(to_kebab_case "$(basename "$dest")")
                    dest="$(dirname "$dest")/$dest_name"

                    move_file_with_log "$file" "$dest" "$reason"
                fi
            done
        else
            # Single file move
            if [ -e "$source_path" ]; then
                local dest="$dest_path"
                # Convert to kebab-case if not keeping in root
                if [ "$dest" != "$source_path" ]; then
                    local dest_name=$(to_kebab_case "$(basename "$dest")")
                    dest="$(dirname "$dest")/$dest_name"
                fi
                move_file_with_log "$source_path" "$dest" "$reason"
            fi
        fi
    done < "$MAPPING_FILE"
    echo ""
}

# Clean empty directories
remove_empty_directories() {
    if [ "$MODE" == "--apply" ]; then
        find . -type d -empty -delete 2>/dev/null
        write_log "Removed empty directories" "SUCCESS"
    else
        local empty_dirs=$(find . -type d -empty 2>/dev/null | wc -l)
        write_log "Would remove $empty_dirs empty directories" "INFO"
    fi
}

# Undo functionality
undo_reorganization() {
    local latest_log=$(ls -t reorg-*.log 2>/dev/null | head -1)

    if [ -z "$latest_log" ]; then
        write_log "No reorg log found to undo" "ERROR"
        exit 1
    fi

    write_log "Undoing changes from: $latest_log" "INFO"

    # Extract moves and reverse order
    grep "MOVED:" "$latest_log" | tac | while read -r line; do
        if [[ "$line" =~ MOVED:\ (.+)\ -\>\ (.+)\ \| ]]; then
            local source="${BASH_REMATCH[2]}"
            local destination="${BASH_REMATCH[1]}"

            if [ -e "$source" ]; then
                local dest_dir=$(dirname "$destination")
                mkdir -p "$dest_dir"
                mv "$source" "$destination"
                write_log "UNDONE: $source -> $destination" "SUCCESS"
            fi
        fi
    done
}

# Main execution
main() {
    write_log "========================================" "INFO"
    write_log "AI Trading Bot Repository Reorganization" "INFO"
    write_log "Mode: $MODE" "INFO"
    write_log "========================================" "INFO"

    case "$MODE" in
        --undo)
            undo_reorganization
            ;;
        --dry-run|--apply)
            # Step 1: Initialize directories
            write_log "Step 1: Initializing directory structure..." "INFO"
            initialize_directories

            # Step 2: Process mapping
            write_log "Step 2: Processing file moves..." "INFO"
            process_mapping

            # Step 3: Clean empty directories
            write_log "Step 3: Cleaning empty directories..." "INFO"
            remove_empty_directories

            # Step 4: Summary
            write_log "========================================" "INFO"
            if [ "$MODE" == "--dry-run" ]; then
                write_log "DRY RUN COMPLETE - No files were moved" "SUCCESS"
                write_log "To apply changes, run: ./reorg-new.sh --apply" "INFO"
            else
                write_log "REORGANIZATION COMPLETE" "SUCCESS"
                write_log "To undo, run: ./reorg-new.sh --undo" "INFO"
            fi
            write_log "Log file: $REORG_LOG" "INFO"
            ;;
        *)
            write_log "Invalid mode. Use --dry-run, --apply, or --undo" "ERROR"
            exit 1
            ;;
    esac
}

# Run main
main