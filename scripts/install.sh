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

fc-cache -fv

if command -v kgx &> /dev/null && command -v gsettings &> /dev/null; then
    if gsettings list-keys org.gnome.Console &> /dev/null; then
        gsettings set org.gnome.Console use-system-font false
        gsettings set org.gnome.Console custom-font 'Source Code Pro KR 12'
        echo "kgx font set to Source Code Pro KR"
    fi
fi

echo "Fonts installed successfully!"
