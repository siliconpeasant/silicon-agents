#!/bin/bash
# =============================================================================
# SoC Build Skill — Setup & MCP Config Helper
# =============================================================================
# 用法:
#   ./setup.sh              安装依赖并打印 MCP 配置
#   ./setup.sh --install    自动写入 Kimi Code MCP 配置 (~/.kimi/mcp.json)
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER="$PROJECT_ROOT/mcp_server.py"
INSTALL_MCP=false

# 解析参数
if [ "$1" = "--install" ] || [ "$1" = "-i" ]; then
    INSTALL_MCP=true
fi

echo "========================================"
echo "  SoC Build Skill Setup"
echo "========================================"
echo "  Project root: $PROJECT_ROOT"
echo "  MCP server:   $MCP_SERVER"
echo "========================================"
echo

# -----------------------------------------------------------------------------
# 1. 检查 Python
# -----------------------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Please install Python 3."
    exit 1
fi

PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
echo "[1/4] Python version: $PYTHON_VER"

# -----------------------------------------------------------------------------
# 2. 安装 Python 依赖
# -----------------------------------------------------------------------------
echo
echo "[2/4] Installing Python dependencies..."

# 检查 pip
if ! python3 -m pip --version &>/dev/null; then
    echo "[WARN] pip not found, trying to install..."
    python3 -m ensurepip --upgrade 2>/dev/null || true
fi

# 安装依赖
PIP_INSTALL="python3 -m pip install"
if python3 -m pip install --help 2>/dev/null | grep -q break-system-packages; then
    PIP_INSTALL="python3 -m pip install --break-system-packages"
fi

$PIP_INSTALL pandas numpy openpyxl xlrd pyyaml mcp 2>&1 | tail -3
echo "      Dependencies installed."

# -----------------------------------------------------------------------------
# 3. 验证 MCP Server
# -----------------------------------------------------------------------------
echo
echo "[3/4] Verifying MCP server..."
if [ ! -f "$MCP_SERVER" ]; then
    echo "[ERROR] MCP server not found: $MCP_SERVER"
    exit 1
fi

python3 -c "from mcp.server.fastmcp import FastMCP; print('      MCP SDK OK')" 2>/dev/null || {
    echo "[ERROR] MCP SDK not available. Please check installation."
    exit 1
}

# -----------------------------------------------------------------------------
# 4. 生成 MCP 配置
# -----------------------------------------------------------------------------
echo
echo "[4/4] MCP Configuration"
echo

MCP_CONFIG='{
  "mcpServers": {
    "soc-build": {
      "command": "python3",
      "args": ["'$MCP_SERVER'"]
    }
  }
}'

if [ "$INSTALL_MCP" = true ]; then
    KIMI_DIR="$HOME/.kimi"
    KIMI_CONFIG="$KIMI_DIR/mcp.json"
    mkdir -p "$KIMI_DIR"

    if [ -f "$KIMI_CONFIG" ]; then
        echo "[INFO] Existing config found: $KIMI_CONFIG"
        echo "[INFO] Backing up to: $KIMI_CONFIG.bak"
        cp "$KIMI_CONFIG" "$KIMI_CONFIG.bak"

        python3 - "$KIMI_CONFIG" "$MCP_SERVER" <<'PYEOF'
import json, sys
config_file = sys.argv[1]
server_path = sys.argv[2]
with open(config_file, 'r') as f:
    config = json.load(f)
config.setdefault('mcpServers', {})
config['mcpServers']['soc-build'] = {
    "command": "python3",
    "args": [server_path]
}
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)
print(f"[OK] MCP config merged: {config_file}")
PYEOF
    else
        echo "$MCP_CONFIG" > "$KIMI_CONFIG"
        echo "[OK] MCP config created: $KIMI_CONFIG"
    fi

    echo
    echo "========================================"
    echo "  Setup complete!"
    echo "========================================"
    echo "  MCP server: $MCP_SERVER"
    echo "  Config:     $KIMI_CONFIG"
    echo
    echo "  Restart your AI assistant to load"
    echo "  the new MCP tools."
    echo "========================================"
else
    echo "Add the following to your MCP config file:"
    echo
    echo "  Kimi Code:          ~/.kimi/mcp.json"
    echo "  Claude Desktop:     ~/Library/Application Support/Claude/claude_desktop_config.json"
    echo "  Cursor:             Settings → MCP → Add Server"
    echo
    echo "---"
    echo "$MCP_CONFIG"
    echo "---"
    echo
    echo "Or run './setup.sh --install' to auto-write Kimi Code config."
fi
