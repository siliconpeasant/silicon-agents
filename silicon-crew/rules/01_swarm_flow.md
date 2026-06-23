# SoC gated design flow

Creating or materially refactoring RTL follows a gated pipeline. The primary agent coordinates; stage-role agents produce RTL/testbench artifacts.

| Stage | Role | Canonical deliverables |
|---|---|---|
| doc | `soc-doc-engineer` | `docs/*.md` or `docs/<module>/*.md` |
| rtl | `soc-rtl-designer` | `de/rtl/<module>.v`, `de/rtl/filelist.f`, `de/syn/<module>.sdc` |
| verif | `soc-verification-engineer` | `dv/tb/tb_<module>.*`, `dv/sim/sim.log` |
| syn | `soc-synthesis-engineer` | `de/syn/<module>_netlist.v`, `de/syn/synth.log` |

RTL specialization:

- CRG: use `soc-crg-engineer` only when the `crg-gen` MCP server is registered. Otherwise report the missing capability; never hand-write generated CRG logic.
- Top integration: use `soc-integrator` and the `soc-integrate` MCP server. Never hand-write an auto-generated top.

Dependencies are `doc -> rtl -> {verif, syn}`. Verification and synthesis may proceed independently after RTL passes. Respect the host runtime's delegation policy; when named agent profiles are unavailable, use the `soc-pipeline` Skill to give a generic subagent the matching stage contract.

Only these artifact roots are valid:

- documentation: `docs/`
- RTL/filelists: `de/rtl/`
- constraints, synthesis and STA: `de/syn/`
- testbench and simulation: `dv/tb/`, `dv/sim/`

Do not create legacy `rtl/`, `constraints/`, root `sim/`, or root `syn/` compatibility directories or symlinks.
