# SoC 设计 4 阶段流水线 (强制 / silicon-crew)

任何 RTL 模块的创建、重构,主 Agent **必须** spawn 对应 subagent;**禁止**主 Agent 自己手写 RTL 或 testbench。

| 阶段 | subagent | 产物 |
|---|---|---|
| 1 文档 | `silicon-crew:soc-doc-engineer` | `docs/design_spec.md`、`interface_spec.md`、`regmap.md`、`verification_plan.md` |
| 2 RTL | `silicon-crew:soc-rtl-designer` *(标准实现)* | `rtl/<module>.v` + `rtl/rtl.f` + `constraints/base.sdc`,verilator `-Wall` lint-clean |
| 3 验证 | `silicon-crew:soc-verification-engineer` | `tb/*.v` + `sim/results/<task>_tb.log`,iverilog + vvp,0 ERROR / 0 MISMATCH |
| 4 综合 | `silicon-crew:soc-synthesis-engineer` | `syn/output/netlist.v` + `timing.rpt` + `area.rpt`,WNS ≥ 0 |

## rtl 阶段的特化实现

rtl 阶段除了通用的 `soc-rtl-designer`,还有两个**特化 agent**——根据场景替换 rtl-designer 使用,产物结构仍然落在 rtl/ + constraints/ 标准目录:

| 特化 agent | 适用场景 | 关键约束 |
|---|---|---|
| `silicon-crew:soc-crg-engineer` | 子模块是 CRG(时钟复位生成),由 Excel 配置驱动 | **必须**用 `crg_gen` MCP 工具,禁止手写时钟分频/复位同步逻辑 |
| `silicon-crew:soc-integrator` | 顶层 workspace,把多个已完成 rtl 的子模块拼成 top | **必须**用 `soc_integrate` MCP 工具,禁止手写顶层 module |

选择规则:
- 普通 RTL 设计(算术/控制/状态机) → `soc-rtl-designer`
- CRG / 时钟复位子系统 → `soc-crg-engineer`(输入是 Excel,不是 spec)
- 顶层集成(已有多个子模块 rtl=done) → `soc-integrator`(顶层 workspace 独立)

特化 agent 完成后 `pipeline_state.json` 里的 rtl 阶段同样标记 `done`,verify / syn 阶段沿用通用 agent。

## 自检

开始任何 RTL 相关动作前,先回答:这一步该 spawn 哪个 subagent?如果答案是"主 Agent 直接 Write 文件",十有八九违规——除非满足例外条款(见 `03_exceptions.md`)。

## 并行机会

同一阶段内的**独立子模块**可并行 spawn 多个相同 subagent(例如多个 `soc-rtl-designer` 同时写不同子模块,然后由主 Agent 拼接顶层)。默认串行,除非用户明确说"并行设计多个模块"。
