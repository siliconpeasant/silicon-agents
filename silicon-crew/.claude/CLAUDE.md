# silicon-crew workflow

Use `rules/01_swarm_flow.md`, `rules/02_toolchain.md`, and `rules/05_pipeline_state.md` as the coordination contract for RTL creation and refactoring.

Core roles are `soc-doc-engineer`, `soc-rtl-designer`, `soc-verification-engineer`, and `soc-synthesis-engineer`. Use `soc-integrator` for generated top-level integration. Use `soc-openroad-engineer` for OpenROAD-flow-scripts physical-design handoff. Use `soc-crg-engineer` only after the `crg-gen` MCP server is registered.

Canonical module artifacts live under `docs/`, `de/rtl/`, `de/syn/`, `de/run/`, `dv/tb/`, and `dv/sim/`. EDA stage execution goes through registered MCP tools; do not use direct shell fallbacks.

Each stage must transition through `in_progress` and may become `done` only with existing artifacts and passing checks recorded in `pipeline_state.json`.
