#!/bin/bash

# MCP Server Startup Script
# Activates Python virtual environment and runs server.py

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env file if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
  export $(cat "$SCRIPT_DIR/.env" | grep -v '#' | grep -v '^$' | xargs)
fi

# Source the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the server
python "$SCRIPT_DIR/server.py"
