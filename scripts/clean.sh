#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Cleaning build artifacts..."

# Remove assets
if [ -d "$PROJECT_DIR/assets" ]; then
    echo "Removing assets/"
    rm -rf "$PROJECT_DIR/assets"
fi

# Remove output
if [ -d "$PROJECT_DIR/out" ]; then
    echo "Removing out/"
    rm -rf "$PROJECT_DIR/out"
fi

echo "Clean completed!"
