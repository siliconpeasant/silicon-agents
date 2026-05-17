#!/usr/bin/env python3
"""检查仿真结果：是否PASS、error/mismatch数量"""
import sys, os, json, re
from pathlib import Path

def check(workspace: str) -> dict:
    results_dir = Path(workspace) / "sim" / "results"
    results = {"logs_checked": [], "errors": 0, "mismatches": 0, "passes": 0}
    issues = []
    
    if not results_dir.exists():
        issues.append("sim/results/ 目录不存在")
        return {"passed": False, "details": results, "issues": issues}
    
    for logfile in results_dir.glob("*.log"):
        content = logfile.read_text()
        results["logs_checked"].append(logfile.name)
        
        # 统计 error / mismatch / PASS
        errors = len(re.findall(r'\\bERROR\\b', content, re.I))
        mismatches = len(re.findall(r'\\bMISMATCH\\b', content, re.I))
        passes = len(re.findall(r'\\bPASS\\b', content, re.I))
        
        results["errors"] += errors
        results["mismatches"] += mismatches
        results["passes"] += passes
        
        if errors > 0:
            issues.append(f"{logfile.name}: 发现 {errors} 个 ERROR")
        if mismatches > 0:
            issues.append(f"{logfile.name}: 发现 {mismatches} 个 MISMATCH")
    
    passed = results["errors"] == 0 and results["mismatches"] == 0 and results["passes"] > 0
    return {"passed": passed, "details": results, "issues": issues}

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check(ws)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["passed"] else 1)
