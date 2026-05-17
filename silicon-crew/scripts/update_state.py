#!/usr/bin/env python3
"""
更新模块或 IP 包 pipeline_state.json 中指定阶段的状态。

单模块模式:
  python3 update_state.py <module_dir> <step> <status> [options]

多子模块模式(IP 包):
  python3 update_state.py <ip_dir> --module <submodule> <step> <status> [options]

Options:
  --artifacts "file1,file2"     产物文件列表(逗号分隔,相对模块根目录)
  --check "tool:passed[:note]"   检查结果
  --note "备注文本"
"""
import sys
import json
import os
import argparse
from datetime import datetime, timezone


def _new_pipeline() -> dict:
    """兼容旧版 state.json 的 pipeline 结构初始化。"""
    return {
        "doc": {"step_id": "doc", "name": "设计文档编写", "agent": "soc-doc-engineer",
                "status": "pending", "started_at": None, "completed_at": None,
                "artifacts": [], "check_results": [], "notes": ""},
        "rtl": {"step_id": "rtl", "name": "RTL设计与编码", "agent": "soc-rtl-designer",
                "status": "pending", "started_at": None, "completed_at": None,
                "artifacts": [], "check_results": [], "notes": ""},
        "verif": {"step_id": "verif", "name": "验证环境搭建与仿真", "agent": "soc-verification-engineer",
                  "status": "pending", "started_at": None, "completed_at": None,
                  "artifacts": [], "check_results": [], "notes": ""},
        "syn": {"step_id": "syn", "name": "逻辑综合与时序分析", "agent": "soc-synthesis-engineer",
                "status": "pending", "started_at": None, "completed_at": None,
                "artifacts": [], "check_results": [], "notes": ""},
    }


def _recompute_blocked(pipeline: dict):
    for step_name, step_info in pipeline.items():
        if step_info.get("status") != "blocked":
            continue
        blocked_by = step_info.get("blocked_by", [])
        if not blocked_by:
            continue
        all_done = all(pipeline.get(dep, {}).get("status") == "done" for dep in blocked_by)
        if all_done:
            step_info["status"] = "pending"
            step_info["blocked_by"] = []


def _compute_next_actions(pipeline: dict) -> list:
    actions = []
    deps_map = {
        "rtl": ["doc"],
        "verif": ["rtl"],
        "syn": ["rtl"],
    }
    for step_name, step_info in pipeline.items():
        status = step_info.get("status")
        if status == "fail":
            actions.append({"stage": step_name, "action": "fix_and_retry",
                            "reason": f"{step_name} failed, needs fix before proceeding"})
        elif status == "pending":
            deps = deps_map.get(step_name, [])
            deps_done = all(pipeline.get(d, {}).get("status") == "done" for d in deps)
            if deps_done:
                actions.append({"stage": step_name, "action": f"spawn {step_info['agent']}",
                                "reason": f"dependencies {deps} satisfied, ready to start {step_name}"})
    return actions


def update_pipeline(pipeline: dict, step: str, status: str,
                    artifacts: list = None, check: str = None, note: str = None):
    if step not in pipeline:
        # 兼容旧版可能缺失阶段的情况
        pipeline[step] = _new_pipeline()[step]

    step_data = pipeline[step]
    step_data["status"] = status
    step_data["last_updated"] = _now()

    if status == "in_progress" and step_data.get("started_at") is None:
        step_data["started_at"] = _now()
    if status in ("done", "fail") and step_data.get("completed_at") is None:
        step_data["completed_at"] = _now()

    if artifacts:
        step_data["artifacts"] = [a.strip() for a in artifacts.split(",") if a.strip()]
    if check:
        parts = check.split(":", 2)
        check_entry = {"tool": parts[0],
                       "passed": parts[1].lower() in ("passed", "pass", "true", "yes") if len(parts) > 1 else None,
                       "note": parts[2] if len(parts) > 2 else ""}
        step_data.setdefault("check_results", []).append(check_entry)
    if note:
        step_data["notes"] = note

    _recompute_blocked(pipeline)


def update_state(module_dir: str, step: str, status: str,
                 submodule: str = None, artifacts: list = None,
                 check: str = None, note: str = None) -> str:
    module_dir = os.path.abspath(module_dir)
    state_path = os.path.join(module_dir, "pipeline_state.json")

    if not os.path.exists(state_path):
        raise FileNotFoundError(f"State file not found: {state_path}. Run init_state.py first.")

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    mode = state.get("mode", "single")

    if mode == "multi_module":
        if not submodule:
            raise ValueError("This is a multi-module IP. Use --module <submodule> to specify which module to update.")
        if submodule not in state["modules"]:
            raise ValueError(f"Submodule '{submodule}' not found. Available: {list(state['modules'].keys())}")
        pipeline = state["modules"][submodule]["pipeline"]
        update_pipeline(pipeline, step, status, artifacts, check, note)
        state["modules"][submodule]["next_actions"] = _compute_next_actions(pipeline)
    else:
        pipeline = state["pipeline"]
        update_pipeline(pipeline, step, status, artifacts, check, note)
        state["next_actions"] = _compute_next_actions(pipeline)

    state["last_updated"] = _now()

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return state_path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update pipeline state")
    parser.add_argument("module_dir", help="模块或 IP 包根目录")
    parser.add_argument("step", choices=["doc", "rtl", "verif", "syn"], help="阶段名")
    parser.add_argument("status", choices=["pending", "in_progress", "done", "fail", "blocked"], help="状态")
    parser.add_argument("--module", default=None, help="子模块名(多模块 IP 包时必须)")
    parser.add_argument("--artifacts", default=None, help="产物文件列表,逗号分隔")
    parser.add_argument("--check", default=None, help="检查结果,格式: tool:passed:note")
    parser.add_argument("--note", default=None, help="备注文本")
    args = parser.parse_args()

    try:
        path = update_state(args.module_dir, args.step, args.status,
                            submodule=args.module, artifacts=args.artifacts,
                            check=args.check, note=args.note)
        mod_info = f" [{args.module}]" if args.module else ""
        print(f"Updated pipeline_state.json:{mod_info} {args.step} -> {args.status}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
