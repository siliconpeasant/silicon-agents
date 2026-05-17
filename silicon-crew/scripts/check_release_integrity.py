#!/usr/bin/env python3
"""检查发布包完整性：manifest与实际文件一致"""
import sys, os, json, hashlib
from pathlib import Path

def checksum(filepath: Path) -> str:
    h = hashlib.sha256()
    h.update(filepath.read_bytes())
    return h.hexdigest()[:16]

def check(workspace: str) -> dict:
    release_dir = Path(workspace) / "release"
    results = {"packages": []}
    issues = []
    
    if not release_dir.exists():
        issues.append("release/ 目录不存在")
        return {"passed": False, "details": results, "issues": issues}
    
    for pkg in release_dir.glob("v*"):
        if not pkg.is_dir():
            continue
        pkg_result = {"version": pkg.name, "files": [], "manifest_ok": False}
        
        manifest = pkg / "manifest.yaml"
        if not manifest.exists():
            issues.append(f"{pkg.name}: manifest.yaml 缺失")
            continue
        
        # 简单检查：manifest中列出的文件都存在
        import yaml
        try:
            mf = yaml.safe_load(manifest.read_text())
            files = mf.get("files", [])
            for f in files:
                fpath = pkg / f
                exists = fpath.exists()
                pkg_result["files"].append({"file": f, "exists": exists})
                if not exists:
                    issues.append(f"{pkg.name}: manifest列出的文件缺失: {f}")
            pkg_result["manifest_ok"] = all(f["exists"] for f in pkg_result["files"])
        except Exception as e:
            issues.append(f"{pkg.name}: manifest解析失败: {e}")
        
        results["packages"].append(pkg_result)
    
    passed = len(issues) == 0 and all(p.get("manifest_ok", False) for p in results["packages"])
    return {"passed": passed, "details": results, "issues": issues}

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check(ws)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["passed"] else 1)
