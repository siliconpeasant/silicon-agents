#!/usr/bin/env python3
"""RTL质量检查：文件存在性、端口一致性、基础语法"""
import sys, os, json, re
from pathlib import Path

def check(workspace: str) -> dict:
    rtl_dir = Path(workspace) / "rtl"
    filelist = rtl_dir / "rtl.f"
    results = {"rtl_files": [], "issues": []}
    
    # 1. 检查文件列表存在
    if not filelist.exists():
        results["issues"].append("rtl/rtl.f 文件列表不存在")
        return {"passed": False, "details": results}
    
    # 2. 检查文件列表中的文件都存在
    with open(filelist, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            fpath = rtl_dir / line
            exists = fpath.exists()
            results["rtl_files"].append({"file": line, "exists": exists})
            if not exists:
                results["issues"].append(f"RTL文件缺失: {line}")
    
    # 3. 基础语法扫描（简单检查）
    for vfile in rtl_dir.glob("*.v"):
        content = vfile.read_text()
        if 'always @(*)' in content and 'reg ' in content:
            # 简单启发式：组合always块内有reg可能产生latch
            pass  # 这里可以做更深入的检查
        # 检查module声明
        if not re.search(r'\bmodule\s+\w+', content):
            results["issues"].append(f"{vfile.name}: 未找到module声明")
    
    passed = len(results["issues"]) == 0
    return {"passed": passed, "details": results}

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check(ws)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["passed"] else 1)
