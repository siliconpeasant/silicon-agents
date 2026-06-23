#!/usr/bin/env bash
set -u

# Consume the hook payload before any early exit.
cat >/dev/null

is_soc=0
if [ -d "${PWD}/chip" ] && [ -d "${PWD}/ip" ]; then
    is_soc=1
elif [ -f "${PWD}/CLAUDE.md" ] && grep -qE "silicon-crew|SoC" "${PWD}/CLAUDE.md" 2>/dev/null; then
    is_soc=1
fi
[ "$is_soc" -eq 1 ] || exit 0

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
plugin_root=${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(dirname "$script_dir")}}
[ -d "$plugin_root/rules" ] || exit 0
export SILICON_CREW_PLUGIN_ROOT=$plugin_root

unset PYTHONHOME PYTHONPATH PYTHONVERSION
export PYTHONIOENCODING=utf-8

exec /usr/bin/python3 - <<'PYEOF'
import json
import os

root = os.environ["SILICON_CREW_PLUGIN_ROOT"]
rules = os.path.join(root, "rules")
context = f"""# silicon-crew SoC workflow

This cwd is a silicon-crew SoC project. For RTL creation or material refactoring:

- Use the gated `doc -> rtl -> {{verif, syn}}` workflow and `pipeline_state.json`.
- Use role agents when the host supports them; otherwise use the `soc-pipeline` Skill with a generic subagent.
- Stage agents must use registered MCP tools. Verification must call `soc-build.soc_sim`; no direct `make`, `iverilog`, `vvp`, or other EDA shell fallback.
- Physical-design handoff uses `soc-openroad`; keep OpenROAD-flow-scripts/OpenROAD directories independent and store project-owned config under `pd/openroad/`.
- Use only `docs/`, `de/rtl/`, `de/syn/`, `de/run/`, `dv/tb/`, and `dv/sim/` artifact roots.
- A stage is done only when artifacts exist and every recorded check passes. Never fabricate simulation PASS or timing WNS/TNS.
- `crg-gen` is currently not registered; do not schedule CRG RTL generation until it is available.

Before acting on an RTL workflow, read the relevant full rules from `{rules}`. Pipeline dispatch requires `01_swarm_flow.md`, `02_toolchain.md`, and `05_pipeline_state.md`; read coding style or exceptions only when applicable.
"""
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}, ensure_ascii=False))
PYEOF
