---
name: soc-pipeline
description: Orchestrate gated SoC RTL creation, refactoring, verification, synthesis, OpenROAD physical-design handoff, CRG routing, and top integration. Use when Codex must create or materially change Verilog/SystemVerilog modules, coordinate stage agents, prepare physical-design handoff, or recover a failed silicon-crew pipeline.
---

# SoC Pipeline

Coordinate work; do not implement RTL or testbench content in the coordinator.

## Preflight

1. Read `../../rules/01_swarm_flow.md`, `../../rules/02_toolchain.md`, and `../../rules/05_pipeline_state.md`. Read coding style or exceptions only when relevant.
2. Resolve the absolute module workspace and module name.
3. Query `pipeline_state.json`; initialize it only when absent. Never overwrite existing state implicitly.
4. Select the RTL role:
   - normal logic: `soc-rtl-designer`
   - top integration: `soc-integrator`
   - CRG: `soc-crg-engineer`, only when `crg-gen` is registered
   - OpenROAD physical-design handoff: `soc-pd-engineer`

## Delegation

Use named role agents when supported. Otherwise spawn a generic subagent with the matching file under `../../agents/` as its role contract. Respect host delegation policy and do not silently replace a required role agent with coordinator-authored RTL.

Every dispatch prompt includes:

- absolute `workspace`
- `task_name`
- objective and approved assumptions
- single- or multi-module state mode
- requirement to update state and quote the `update_state.py` stdout line

After each role returns, query state immediately and verify status, artifacts, and all checks. Do not dispatch downstream work after failure.

## Execution contract

- Canonical paths: `docs/`, `de/rtl/`, `de/syn/`, `dv/tb/`, `dv/sim/`.
- EDA execution uses registered MCP tools. Verification calls `soc-build.soc_sim`; synthesis calls `soc-build.soc_syn`; physical-design handoff calls `soc-openroad.soc_openroad_*`. No direct EDA shell fallback.
- `doc -> rtl`; verification and synthesis may run independently after RTL passes.
- Treat estimated timing and synthetic PASS markers as failures of validation integrity.
- For an approved doc-stage exception, record `doc skipped` with a concrete note before starting RTL.

Stop and report a precise blocker if required MCP capability, an approved interface decision, or an EDA dependency is unavailable.
