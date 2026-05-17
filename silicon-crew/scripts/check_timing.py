#!/usr/bin/env python3
"""检查时序收敛：从timing.rpt中提取WNS"""
import sys, os, json, re
from pathlib import Path

def check(workspace: str) -> dict:
    rpt = Path(workspace) / "syn" / "reports" / "timing.rpt"
    results = {"wns": None, "tns": None, "violations": 0}
    issues = []
    
    if not rpt.exists():
        issues.append("syn/reports/timing.rpt 不存在")
        return {"passed": False, "details": results, "issues": issues}
    
    content = rpt.read_text()
    
    # 尝试提取 WNS
    wns_match = re.search(r'WNS\s*[:=]?\s*([-\d.]+)', content, re.I)
    if wns_match:
        results["wns"] = float(wns_match.group(1))
    
    # 尝试提取 TNS
    tns_match = re.search(r'TNS\s*[:=]?\s*([-\d.]+)', content, re.I)
    if tns_match:
        results["tns"] = float(tns_match.group(1))
    
    # 检查时序违规
    if results["wns"] is not None and results["wns"] < 0:
        issues.append(f"WNS = {results['wns']}ns，时序未收敛")
    elif results["wns"] is None:
        issues.append("无法从报告中提取WNS")
    
    passed = results["wns"] is not None and results["wns"] >= 0
    return {"passed": passed, "details": results, "issues": issues}

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check(ws)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["passed"] else 1)
