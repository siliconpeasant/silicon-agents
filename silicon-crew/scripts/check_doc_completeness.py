#!/usr/bin/env python3
"""检查文档完整性：design_spec, interface_spec, regmap 是否存在"""
import sys, os, json

def check(workspace: str) -> dict:
    required = {
        "design_spec": "docs/design_spec.md",
        "interface_spec": "docs/interface_spec.md",
        "regmap": "docs/regmap.md"
    }
    results = {}
    all_pass = True
    for name, rel in required.items():
        path = os.path.join(workspace, rel)
        exists = os.path.exists(path)
        results[name] = {"path": rel, "exists": exists}
        if not exists:
            all_pass = False
    return {"passed": all_pass, "details": results}

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check(ws)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["passed"] else 1)
