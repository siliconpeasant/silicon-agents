# SoC 工具链与 skill 优先 (强制)

涉及 Verilog 端口提取、顶层集成、wrapper 生成、filelist 生成、lint 检查等场景,**必须**优先调用对应 skill 的 MCP 工具。**禁止**手写 Python/Bash 脚本重复造轮子。

## 常用工具映射（按 skill 分组）

| 任务 | Skill | Tool |
|---|---|---|
| 项目脚手架 | `soc-build` | `soc_init` / `soc_add_chip` / `soc_add_ip` |
| 生成 filelist | `soc-build` | `soc_flist` |
| Lint 检查 | `soc-build` | `soc_lint` |
| 编译仿真 | `soc-build` | `soc_comp` |
| 提取 Verilog 模块端口 | `soc-integrate` | `soc_extract` |
| 实例化代码生成 | `soc-integrate` | `soc_instantiate` |
| 顶层模块集成 | `soc-integrate` | `soc_integrate` |
| 信号 wrapper | `soc-integrate` | `soc_wrap` |
| 端口表 CSV 导出 | `soc-integrate` | `soc_csv` |
| 端口快照 / 变更追踪 | `soc-integrate` | `soc_snapshot` / `soc_diff` / `soc_update` |
| 顶层端口连接提取 | `soc-integrate` | `soc_extract_map` |
| 删除模块并刷新顶层 | `soc-integrate` | `soc_remove` |
| YAML → 寄存器 RTL | `yml2reg` | `yml2reg` |
| Excel 寄存器表 → YAML | `excel-yml-gen` | `excel_yml_gen` |
| CRG 需求表 → 设计表 | `crg-req-to-design` | `crg_req_to_design` |
| 时钟/复位拓扑图 | `cr-tree-diag-gen` | `cr_tree_diag_gen` / `cr_tree_diag_gen_drawio` / `cr_tree_diag_gen_excalidraw` |

> 注：`crg_gen`（CRG RTL 生成）、`io_top_gen`（IO/Pad 生成）、`gen_asic_memmap`（Memory Map 生成）、`gen_memwrap`（Memory Wrapper 生成）等工具属于 `crg-gen` skill，当前未在 plugin.json 注册，如需使用请手动添加。

## EDA 工具底层

- **Lint**: `verilator --lint-only -Wall`(通常通过 `soc_lint` 包装)
- **仿真**: `iverilog` + `vvp`(通常通过 `soc_comp` 包装)
- **综合**: `yosys`(由 `silicon-crew:soc-synthesis-engineer` 调度)

底层 EDA 命令优先让封装好的工具/subagent 调用,不要绕过封装直接命令行。

## Lint 必须走项目封装(强制)

Lint 检查**禁止**直接调用 `verilator --lint-only <single-file>`。必须通过以下方式之一执行:

1. **`mcp__plugin_silicon-crew_soc-build__soc_lint`**(MCP 工具,优先)
2. **项目 `make lint`**(如 `make lint [RTL_TOP=xxx]`)

严禁的行为包括且不限于:
- 直接 `verilator --lint-only -Wall rtl/single_file.v`
- 跳过 `--top-module` 标志直接对单个模块做 lint
- 跳过项目 filelist 而只 lint 自己写的那一个文件

原因:
- 项目级 lint 会按 filelist 全量编译,暴露跨模块问题(timescale 不一致、命名冲突、参数覆盖、include 路径错误等)
- 单文件 lint 永远无法发现多模块集成错误
- 项目 `make lint` 会落 `de/run/lint.log` 审计痕迹

RTL 写完后,**必须通过项目 make lint 再次验证**,以实际 make lint 输出为 lint clean 的唯一判定标准。subagent 自己调 verilator 单文件的结果**不算**。

## 仿真必须走项目封装(强制)

编译仿真**禁止**直接调用 `iverilog <single-file>` 或 `vvp <outfile>`。必须通过以下方式之一执行:

1. **`mcp__plugin_silicon-crew_soc-build__soc_comp`**(MCP 工具,优先)
2. **项目 `make sim`**(如 `make sim SIMULATOR=iverilog TOP_MODULE=tb_xxx`)

严禁的行为包括且不限于:
- 直接 `iverilog -g2012 -o sim.out rtl/single_file.v tb/single_tb.v`
- 跳过 `make comp` 阶段直接 `vvp` 运行
- 绕过项目 filelist 和路径替换自行硬编码文件列表

原因:
- 项目 Makefile 统一管理 filelist、路径替换(`$SOC`)、simulator 切换(iverilog/verilator/vcs/xcelium)
- 跳过封装会导致路径错误、依赖缺失、simulator 配置不一致

## 综合必须走项目封装(强制)

综合**禁止**直接调用 `yosys syn.ys` 或手写 yosys 脚本。必须通过以下方式之一执行:

1. **项目 `make syn`**(如 `make syn RTL_TOP=xxx`)
2. **由 `silicon-crew:soc-synthesis-engineer` 按项目 Makefile 框架执行**

严禁的行为包括且不限于:
- 直接 `cd syn/ && yosys -s syn.ys`
- 手写 yosys 脚本而不用项目 Makefile 的 syn 目标
- 跳过 `hierarchy -check -top $(RTL_TOP)` 等标准流程
- 生成网表到项目约定目录之外的任意位置

原因:
- 项目 `make syn` 自动处理 filelist 生成、路径替换、标准 yosys 流程
- 直接调用 yosys 会导致脚本碎片化、流程不可复现、产物目录不一致
- 综合产物(netlist、report、SDC)必须落到项目约定目录,供下游 review 和发布
