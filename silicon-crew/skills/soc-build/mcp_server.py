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
    name="soc-build",
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
def soc_init(project_name: str, output_dir: str = ".", top_module: str = "") -> str:
    """初始化标准化 SoC 项目目录结构。

    Args:
        project_name: 项目名称（同时作为目录名和默认顶层模块前缀）
        output_dir: 输出父目录，默认当前目录
        top_module: 顶层模块名，留空则使用 <project_name>_top
    """
    args = ["init", project_name, "-o", output_dir]
    if top_module:
        args += ["-t", top_module]
    return _python("soc_project_init.py", *args)


@mcp.tool()
def soc_add_ip(ip_name: str, project_dir: str, ip_type: str = "digital") -> str:
    """在项目中新增 IP 模块。

    Args:
        ip_name: IP 模块名
        project_dir: 项目根目录路径
        ip_type: IP 类型，可选 digital 或 third_party
    """
    return _python("soc_project_init.py", "add_ip", ip_name, "-p", project_dir, "-t", ip_type)


@mcp.tool()
def soc_add_chip(module_name: str, project_dir: str) -> str:
    """在 chip/ 目录下新增子模块。

    Args:
        module_name: 子模块名，如 core / bus / periph
        project_dir: 项目根目录路径
    """
    return _python("soc_project_init.py", "add_chip", module_name, "-p", project_dir)


@mcp.tool()
def soc_flist(path: str, output: str = "", recursive: bool = False) -> str:
    """递归扫描目录生成 Verilog filelist（.f）。

    Args:
        path: 待扫描的目录路径
        output: 输出 filelist 文件路径，留空则打印到 stdout
        recursive: 是否递归扫描子目录
    """
    args = [path]
    if output:
        args += ["-o", output]
    if recursive:
        args += ["-r"]
    return _python("soc_gen_flist.py", *args)


@mcp.tool()
def soc_lint(module_dir: str, lint_tool: str = "verilator") -> str:
    """对指定模块执行 lint 检查。

    Args:
        module_dir: 包含 Makefile 的模块目录（如 chip/top 或 ip/digital/xxx）
        lint_tool: lint 工具，可选 verilator 或 iverilog
    """
    return _run(
        ["make", "lint", f"LINT_TOOL={lint_tool}"],
        cwd=module_dir,
    )


@mcp.tool()
def soc_comp(module_dir: str, simulator: str = "iverilog") -> str:
    """编译仿真指定模块。

    Args:
        module_dir: 包含 Makefile 的模块目录
        simulator: 仿真器，可选 iverilog / vcs / verilator / xcelium
    """
    return _run(
        ["make", "comp", f"SIMULATOR={simulator}"],
        cwd=module_dir,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SoC Build MCP Server")
    parser.add_argument("--sse", action="store_true", help="使用 SSE (HTTP) transport")
    args = parser.parse_args()

    transport = "sse" if args.sse else "stdio"
    mcp.run(transport=transport)
