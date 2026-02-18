#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
ASSETS_DIR="$PROJECT_DIR/assets"

# Font versions
D2CODING_VERSION="1.3.2"
D2CODING_DATE="20180524"
SOURCE_CODE_PRO_VERSION="2.042R-u/1.062R-i/1.026R-vf"

# OS Detection
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [ -f /etc/arch-release ]; then
    OS="arch"
elif [ -f /etc/lsb-release ] || [ -f /etc/debian_version ]; then
    OS="ubuntu"
else
    echo "Warning: Unsupported OS detected ($OSTYPE). Trying generic Linux path..."
    OS="linux"
fi

echo "Source Code Pro KR - Environment Setup"
echo "========================================"
echo "Project directory: $PROJECT_DIR"
echo "Detected OS: $OS"
echo ""

# Install dependencies
echo "Checking dependencies..."
if [ "$OS" == "macos" ]; then
    if ! command -v brew &> /dev/null; then
        echo "Error: Homebrew is not installed. Please install from https://brew.sh"
        exit 1
    fi
    
    for pkg in fontforge python unzip curl; do
        if ! command -v $pkg &> /dev/null; then
            echo "Installing $pkg via Homebrew..."
            brew install $pkg --quiet
        fi
    done
elif [ "$OS" == "arch" ]; then
    if ! command -v pacman &> /dev/null; then
        echo "Error: pacman not found"
        exit 1
    fi
    
    NEEDED_PKGS=()
    for pkg in fontforge python unzip curl; do
        if ! command -v $pkg &> /dev/null; then
            NEEDED_PKGS+=("$pkg")
        fi
    done
    
    if [ ${#NEEDED_PKGS[@]} -gt 0 ]; then
        echo "Installing missing packages: ${NEEDED_PKGS[*]}..."
        sudo pacman -S --needed --noconfirm "${NEEDED_PKGS[@]}"
    fi
elif [ "$OS" == "ubuntu" ]; then
    if ! command -v apt-get &> /dev/null; then
        echo "Error: apt-get not found"
        exit 1
    fi
    
    echo "Updating package list..."
    sudo apt-get update -qq
    
    NEEDED_PKGS=()
    # Check for core commands
    for pkg_cmd in fontforge:fontforge python3:python3 unzip:unzip curl:curl; do
        IFS=":" read -r pkg cmd <<< "$pkg_cmd"
        if ! command -v "$cmd" &> /dev/null; then
            NEEDED_PKGS+=("$pkg")
        fi
    done
    
    # Always check for python3-venv on Ubuntu as it's often missing
    if ! dpkg -l | grep -q "python3-venv"; then
        NEEDED_PKGS+=("python3-venv")
    fi
    
    if [ ${#NEEDED_PKGS[@]} -gt 0 ]; then
        echo "Installing missing packages: ${NEEDED_PKGS[*]}..."
        sudo apt-get install -y -qq "${NEEDED_PKGS[@]}"
    fi
fi

# Check Python command
if [ "$OS" == "macos" ]; then
    if [ -x "/opt/homebrew/bin/python3" ]; then
        PYTHON_CMD="/opt/homebrew/bin/python3"
    elif [ -x "/usr/local/bin/python3" ]; then
        PYTHON_CMD="/usr/local/bin/python3"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD=$(command -v python3)
    else
        echo "Error: Python 3 not found. Please install via Homebrew."
        exit 1
    fi
else
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=$(command -v python3)
    elif command -v python &> /dev/null; then
        PYTHON_CMD=$(command -v python)
    else
        echo "Error: Python not found"
        exit 1
    fi
fi
echo "Using: $PYTHON_CMD ($($PYTHON_CMD --version))"
echo "Using FontForge: $(fontforge --version | head -n1)"
echo ""

# Create venv with system-site-packages for fontforge
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with system-site-packages..."
    "$PYTHON_CMD" -m venv --system-site-packages "$VENV_DIR"
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi
echo ""

# Upgrade pip
echo "Upgrading pip..."
"$VENV_DIR/bin/pip3" install --upgrade pip --quiet
echo "pip upgraded"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
    echo "Dependencies installed"
else
    echo "No requirements.txt found"
fi
echo ""

# Download fonts
echo "Downloading font files..."
cd "$PROJECT_DIR"

# Create assets directory
mkdir -p "$ASSETS_DIR"

# Download Source Code Pro
echo "[INFO] Download Source Code Pro"
curl -sL "https://github.com/adobe-fonts/source-code-pro/releases/download/${SOURCE_CODE_PRO_VERSION}/TTF-source-code-pro-2.042R-u_1.062R-i.zip" -o "$ASSETS_DIR/source-code-pro.zip"

# Download D2Coding (contains all variants including ligature)
echo "[INFO] Download D2 Coding"
curl -sL "https://github.com/naver/d2codingfont/releases/download/VER${D2CODING_VERSION}/D2Coding-Ver${D2CODING_VERSION}-${D2CODING_DATE}.zip" -o "$ASSETS_DIR/D2_Coding.zip"

echo ""
echo "[INFO] Extract Source Code Pro"
unzip -qo "$ASSETS_DIR/source-code-pro.zip" -d "$ASSETS_DIR/"

echo "[INFO] Extract D2 Coding"
unzip -qo "$ASSETS_DIR/D2_Coding.zip" -d "$ASSETS_DIR/"

echo ""
echo "Cleaning up zip files..."
rm "$ASSETS_DIR/source-code-pro.zip"
rm "$ASSETS_DIR/D2_Coding.zip"

echo ""
echo "Environment setup completed!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To build fonts, run:"
echo "  ./scripts/build.sh build"
