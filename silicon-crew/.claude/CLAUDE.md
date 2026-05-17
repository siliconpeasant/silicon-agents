# SoC 前端设计工作流 (silicon-crew plugin)

> 本项目已升级为 Claude Code plugin 型架构。老 Python swarm 框架已废弃,请使用 `soc-*` subagent 执行全流程。

## 架构

- **主 Agent(你)**:编排 + 调度,串行或并行 spawn subagent
- **5 个 subagent(插件提供)**:
  | subagent | 阶段 | 产物 |
  |----------|------|------|
  | `soc-doc-engineer` | 文档 | `docs/*.md` |
  | `soc-rtl-designer` | RTL | `rtl/*.v` + `rtl/rtl.f` + `constraints/base.sdc` |
  | `soc-verification-engineer` | 验证 | `tb/*.v` + `sim/results/*.log` |
  | `soc-synthesis-engineer` | 综合 | `syn/output/netlist.v` + 报告 |
  | `soc-release-engineer` | 发布 | `release/v1.0.0/` 完整包 |

## 编排顺序(串行)

用户提出需求 → **doc** → **rtl** → **verify** → **syn** → **release**

每阶段 spawn 对应 subagent,等它自检 PASS 后进入下一阶段。如果自检失败,主 Agent 分析原因、spawn 修复者或直接自己修。

## 并行机会

- 同一阶段内的**独立子模块**可并行 spawn 多个相同 subagent(例如多个 rtl-designer 同时写不同子模块,然后由 top-integrator 拼)
- 当前版本默认串行,除非用户明确说"并行设计多个模块"

## Workspace 路径

所有产物统一放在:
```
${PWD}/workspace/<task_name>/
```

其中 `<task_name>` 由用户在需求中指定,或由主 Agent 推导(模块名,小写下划线)。

## 废弃项(不要再用)

- ❌ `swarm_create_task`(MCP) — 直接创建 workspace 目录即可
- ❌ `swarm_run_background` — 跑不起来(Planner 写死读 OPENAI_KEY 的 bug)
- ❌ `swarm_legacy_step` — 老状态机,state.json 永远显示 pending
- ❌ `mcp__silicon-crew__swarm_execute_tool` — EDA 工具请直接 Bash 调用
- ❌ `agents/*.py`、`planner/`、`swarm.py` 等 Python 代码 — 已清理

## 质量门禁

每阶段产物必须通过对应 check 脚本:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_doc_completeness.py <workspace>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_rtl_quality.py <workspace>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_sim_pass.py <workspace>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_timing.py <workspace>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_release_integrity.py <workspace>
```

## 快速启动模板

当用户说"设计一个 X 模块"时,主 Agent 按下面执行:

1. 确定 `task_name`(小写下划线,如 `mux2_1`)
2. `mkdir -p workspace/<task_name>/docs`
3. spawn `soc-doc-engineer`,prompt 里传 `task_name` + 用户需求
4. doc 自检 PASS → spawn `soc-rtl-designer`
5. rtl 自检 PASS → spawn `soc-verification-engineer`
6. sim 自检 PASS → spawn `soc-synthesis-engineer`
7. timing PASS → **向用户输出阶段总结**,包含:
   - 各阶段状态(doc/rtl/verif/syn)
   - 关键交付物清单
   - 验证结果(仿真PASS,时序WNS/TNS)
   等待用户确认"总结无误"
8. 用户确认总结后 → **询问用户"是否执行发布打包?"**
9. 用户确认发布 → spawn `soc-release-engineer`
10. 报告最终交付物路径

---
*silicon-crew@siliconpeasant v1.0.0 — 2026-05-17*
