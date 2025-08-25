#!/bin/bash
# Sonph-Code - Claude Code clone launcher script
# Usage: sonph-code [directory]

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Handle help flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "🤖 Sonph-Code - Claude Code Clone"
    echo ""
    echo "Usage:"
    echo "  sonph-code           # Run in current directory"
    echo "  sonph-code /path     # Run in specified directory"
    echo "  sonph-code --help    # Show this help"
    echo ""
    echo "The tool will start with the working directory set to the specified"
    echo "directory (or current directory if none specified)."
    exit 0
fi

# Determine the working directory
if [ $# -gt 0 ]; then
    # Directory specified as argument
    if [ ! -d "$1" ]; then
        echo "❌ Error: Directory '$1' does not exist or is not accessible"
        exit 1
    fi
    WORKING_DIR="$(realpath "$1")"
else
    # Use current working directory
    WORKING_DIR="$(pwd)"
fi

echo "🚀 Starting Sonph-Code in: $WORKING_DIR"

# Change to the working directory
cd "$WORKING_DIR"

# Change to script directory to run uv
cd "$SCRIPT_DIR"

# Run the main.py using uv with the working directory preserved
INITIAL_DIR="$WORKING_DIR" uv run python main.py