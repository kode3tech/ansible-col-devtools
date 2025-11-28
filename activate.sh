#!/bin/bash
# Script to activate the virtual environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    
    echo "Installing dependencies..."
    "$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
    "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Activating virtual environment..."
source "$SCRIPT_DIR/.venv/bin/activate"

echo ""
echo "Virtual environment activated!"
echo "Ansible version: $(ansible --version | head -n 1)"
echo "Python version: $(python --version)"
echo ""
echo "To deactivate, run: deactivate"
