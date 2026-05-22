#!/usr/bin/env bash
# silicon-crew plugin SessionStart hook
# Detect SoC project, then load all rules/*.md from the plugin and inject
# their content into the session via hookSpecificOutput.additionalContext.

set -u

# 1. Detect SoC project (chip/+ip/ both exist, or CLAUDE.md mentions "SoC swarm")
is_soc=0
if [ -d "${PWD}/chip" ] && [ -d "${PWD}/ip" ]; then
    is_soc=1
elif [ -f "${PWD}/CLAUDE.md" ] && grep -qE "silicon-crew|硅工组|SoC swarm" "${PWD}/CLAUDE.md" 2>/dev/null; then
    is_soc=1
fi

if [ "$is_soc" -eq 0 ]; then
    exit 0
fi

# 2. Sanity check: rules directory must exist
if [ -z "${CLAUDE_PLUGIN_ROOT:-}" ] || [ ! -d "${CLAUDE_PLUGIN_ROOT}/rules" ]; then
    exit 0
fi

# 3. Concatenate rules/*.md and emit JSON via python3
export PYTHONIOENCODING=utf-8
exec python3 - <<'PYEOF'
import glob
import json
import os
import sys

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
rules_dir = os.path.join(plugin_root, "rules")
files = sorted(glob.glob(os.path.join(rules_dir, "*.md")))

if not files:
    sys.exit(0)

header = (
    "# SoC 设计强制规范 (silicon-crew plugin · SessionStart 自动注入)\n\n"
    f"当前 cwd 已识别为 SoC 项目。本会话所有后续工作必须遵守以下规范 (共 {len(files)} 章, 来自 {rules_dir}):\n"
)
sections = [header]
for path in files:
    name = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as fh:
        body = fh.read().rstrip("\n")
    sections.append(f"<!-- {name} -->\n{body}")

context = "\n\n---\n\n".join(sections)

out = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}
print(json.dumps(out, ensure_ascii=False))
PYEOF
