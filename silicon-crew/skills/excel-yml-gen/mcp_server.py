#!/usr/bin/env python3
"""
SoC Build MCP Server

轻量级 MCP Wrapper，暴露最常用的 soc-build 工具操作。
底层仍调用 scripts/ 目录下的现有 CLI 脚本，不改动原有逻辑。

运行方式:
    python3 mcp_server.py          # stdio transport (默认)
    python3 mcp_server.py --sse    # SSE transport (HTTP)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# 路径推导
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent / "scripts"


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="excel-yml-gen",
    instructions=(
        "SoC 前端 RTL 集成与自动化生成工具集。\n"
        "支持项目初始化、Verilog 端口提取、顶层集成、寄存器/CRG/IO 生成、"
        "filelist 生成、lint 检查等功能。"
    ),
)


def _run(cmd: list[str], cwd: str = None, timeout: int = 120) -> str:
    """运行外部命令，统一捕获 stdout/stderr。"""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
    )
    out = result.stdout or ""
    if result.stderr:
        out += "\n[stderr]\n" + result.stderr
    if result.returncode != 0:
        out += f"\n[exit code: {result.returncode}]"
    return out


def _python(script: str, *args: str, cwd: str = None) -> str:
    """调用 scripts/ 目录下的 Python 脚本。"""
    return _run([sys.executable, str(SCRIPT_DIR / script)] + list(args), cwd=cwd)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def excel_yml_gen(excel_file: str, sheet_name: str, output_dir: str = ".") -> str:
    """从 Excel 寄存器描述生成 YAML 和 Verilog regfile。

    Args:
        excel_file: Excel 文件路径
        sheet_name: sheet 名称（如 demo_sys_ctrl_reg，会自动去掉 _reg 后缀）
        output_dir: 输出目录，默认当前目录
    """
    return _python("excel_yml_gen.py", excel_file, sheet_name, output_dir)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SoC Build MCP Server")
    parser.add_argument("--sse", action="store_true", help="使用 SSE (HTTP) transport")
    args = parser.parse_args()

    transport = "sse" if args.sse else "stdio"
    mcp.run(transport=transport)
