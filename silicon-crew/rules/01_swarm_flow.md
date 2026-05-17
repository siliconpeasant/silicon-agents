# SoC 设计 5 阶段流水线 (强制 / silicon-crew)

任何 RTL 模块的创建、重构,主 Agent **必须** spawn 对应 subagent;**禁止**主 Agent 自己手写 RTL 或 testbench。

| 阶段 | subagent | 产物 |
|---|---|---|
| 1 文档 | `silicon-crew:soc-doc-engineer` | `docs/design_spec.md`、`interface_spec.md`、`regmap.md`、`verification_plan.md` |
| 2 RTL | `silicon-crew:soc-rtl-designer` | `rtl/<module>.v` + `rtl/rtl.f` + `constraints/base.sdc`,verilator `-Wall` lint-clean |
| 3 验证 | `silicon-crew:soc-verification-engineer` | `tb/*.v` + `sim/results/<task>_tb.log`,iverilog + vvp,0 ERROR / 0 MISMATCH |
| 4 综合 | `silicon-crew:soc-synthesis-engineer` | `syn/output/netlist.v` + `timing.rpt` + `area.rpt`,WNS ≥ 0 |
| 5 发布 | `silicon-crew:soc-release-engineer` | `release/v1.0.0/` + `manifest.yaml` + `checksums.txt` + `RELEASE_NOTES.md` |

## 自检

开始任何 RTL 相关动作前,先回答:这一步该 spawn 哪个 subagent?如果答案是"主 Agent 直接 Write 文件",十有八九违规——除非满足例外条款(见 `03_exceptions.md`)。

## 并行机会

同一阶段内的**独立子模块**可并行 spawn 多个相同 subagent(例如多个 `soc-rtl-designer` 同时写不同子模块,然后由主 Agent 拼接顶层)。默认串行,除非用户明确说"并行设计多个模块"。
