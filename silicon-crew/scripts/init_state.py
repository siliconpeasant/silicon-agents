#!/usr/bin/env python3
"""
初始化模块或 IP 包的 pipeline_state.json。

单模块模式:
  python3 init_state.py <module_dir> [module_name]

多子模块模式(IP 包):
  python3 init_state.py <ip_dir> --submodules "mod1,mod2,mod3"
"""
import sys
import json
import os
from datetime import datetime, timezone


def _new_pipeline() -> dict:
    return {
        "doc": {
            "step_id": "doc",
            "name": "设计文档编写",
            "agent": "soc-doc-engineer",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "artifacts": [],
            "check_results": [],
            "notes": ""
        },
        "rtl": {
            "step_id": "rtl",
            "name": "RTL设计与编码",
            "agent": "soc-rtl-designer",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "artifacts": [],
            "check_results": [],
            "notes": ""
        },
        "verif": {
            "step_id": "verif",
            "name": "验证环境搭建与仿真",
            "agent": "soc-verification-engineer",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "artifacts": [],
            "check_results": [],
            "notes": ""
        },
        "syn": {
            "step_id": "syn",
            "name": "逻辑综合与时序分析",
            "agent": "soc-synthesis-engineer",
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "artifacts": [],
            "check_results": [],
            "notes": ""
        }
    }


def init_state_single(module_dir: str, module_name: str = None) -> str:
    module_dir = os.path.abspath(module_dir)
    module_name = module_name or os.path.basename(os.path.normpath(module_dir))

    state = {
        "module": module_name,
        "workspace": module_dir,
        "mode": "single",
        "created_at": _now(),
        "last_updated": _now(),
        "pipeline": _new_pipeline(),
        "next_actions": []
    }

    state_path = os.path.join(module_dir, "pipeline_state.json")
    os.makedirs(module_dir, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return state_path


def init_state_multi(ip_dir: str, submodules: list, ip_name: str = None) -> str:
    ip_dir = os.path.abspath(ip_dir)
    ip_name = ip_name or os.path.basename(os.path.normpath(ip_dir))

    modules = {}
    for mod in submodules:
        modules[mod] = {
            "pipeline": _new_pipeline(),
            "next_actions": []
        }

    state = {
        "ip": ip_name,
        "workspace": ip_dir,
        "mode": "multi_module",
        "created_at": _now(),
        "last_updated": _now(),
        "modules": modules,
        "next_actions": []
    }

    state_path = os.path.join(ip_dir, "pipeline_state.json")
    os.makedirs(ip_dir, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return state_path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize module or IP package pipeline_state.json"
    )
    parser.add_argument("target_dir", help="Module or IP package directory")
    parser.add_argument("name", nargs="?", help="Module name (single) or IP name (multi)")
    parser.add_argument(
        "--submodules",
        help='Comma-separated submodule list for multi-module mode, e.g. "mod1,mod2,mod3"',
    )
    args = parser.parse_args()

    if args.submodules:
        submodules = [s.strip() for s in args.submodules.split(",") if s.strip()]
        path = init_state_multi(args.target_dir, submodules, args.name)
        print(f"Created multi-module pipeline_state.json: {path}")
        print(f"Submodules: {', '.join(submodules)}")
    else:
        path = init_state_single(args.target_dir, args.name)
        print(f"Created pipeline_state.json: {path}")
