#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment and run the script
source "$SCRIPT_DIR/venv/bin/activate"
exec python "$SCRIPT_DIR/speech_to_text.py"
