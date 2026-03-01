#!/bin/bash
# fund-advisor CLI 脚本
# 调用 tools 中的 fund-tools 命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TOOLS_DIR="$PROJECT_ROOT/tools"

# Check if venv exists, if not create and install
if [ ! -d "$TOOLS_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$TOOLS_DIR/venv"
    echo "Installing fund-tools..."
    "$TOOLS_DIR/venv/bin/pip" install -e "$TOOLS_DIR" -q
fi

# Run the installed command
"$TOOLS_DIR/venv/bin/fund-tools" "$@"