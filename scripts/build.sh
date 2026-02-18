#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

# Check venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found"
    echo "Run: ./scripts/setup-env.sh"
    exit 1
fi

# Check if assets exist
if [ ! -d "$PROJECT_DIR/assets/TTF" ]; then
    echo "Error: Font assets not found"
    echo "Run: ./scripts/setup-env.sh"
    exit 1
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Run build script
cd "$PROJECT_DIR"
python3 "$PROJECT_DIR/src/main.py"
