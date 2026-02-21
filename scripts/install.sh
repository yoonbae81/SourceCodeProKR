#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$PROJECT_DIR/out"

# Check if output directory exists
if [ ! -d "$OUT_DIR" ]; then
    echo "Error: Output directory not found"
    echo "Run: ./scripts/build.sh first"
    exit 1
fi

# Check if any ttf files exist
if [ ! -f "$OUT_DIR"/*.ttf ]; then
    echo "Error: No .ttf files found in $OUT_DIR"
    echo "Run: ./scripts/build.sh first"
    exit 1
fi

# Create font directory
mkdir -p ~/.local/share/fonts

# Copy font files
cp "$OUT_DIR"/*.ttf ~/.local/share/fonts/

# Refresh font cache
fc-cache -fv

echo "Fonts installed successfully!"
