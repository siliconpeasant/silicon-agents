# SoC 前端设计工作流 (silicon-crew plugin)

> 本项目已升级为 Claude Code plugin 型架构。老 Python swarm 框架已废弃,请使用 `soc-*` subagent 执行全流程。

## 架构

- **主 Agent(你)**:编排 + 调度,串行或并行 spawn subagent
- **4 个核心 subagent(插件提供)**:
  | subagent | 阶段 | 产物 |
  |----------|------|------|
  | `soc-doc-engineer` | 文档 | `docs/*.md` |
  | `soc-rtl-designer` | RTL | `rtl/*.v` + `rtl/rtl.f` + `constraints/base.sdc` |
  | `soc-verification-engineer` | 验证 | `tb/*.v` + `sim/results/*.log` |
  | `soc-synthesis-engineer` | 综合 | `syn/output/netlist.v` + 报告 |
- **2 个 rtl 阶段特化 subagent**:
  | subagent | 触发场景 | 关键约束 |
  |----------|---------|---------|
  | `soc-crg-engineer` | 子模块是 CRG(时钟复位生成),从 Excel 配置驱动 | **必须用 `crg_gen` MCP 工具**生成,禁止手写 |
  | `soc-integrator` | 顶层 workspace,需要把多个 rtl=done 的子模块拼成 top | **必须用** MCP `soc_add_chip`(建项目内模块目录)+ `soc_integrate`(top.v)+ `soc_flist`(filelist.f);**filelist.mk 用 `include $(PROJECT_ROOT)/<sub>/de/rtl/filelist.mk` 声明依赖**,严格遵循 skill 模板的 include guard + MODULE_FILELISTS 去重模式;**子模块不拷贝** |

## 编排顺序(串行)

用户提出需求 → **doc** → **rtl** → **verify** → **syn**

每阶段 spawn 对应 subagent,等它自检 PASS 后进入下一阶段。如果自检失败,主 Agent 分析原因、spawn 修复者或直接自己修。

## 并行机会

- 同一阶段内的**独立子模块**可并行 spawn 多个相同 subagent(例如多个 rtl-designer 同时写不同子模块,然后由 top-integrator 拼)
- **`soc-integrator` 与子模块的 verify/syn 并行**:子模块 rtl=done 后即可启动集成,子模块的 verify/syn 在后台并行进行
- 当前版本默认串行,除非用户明确说"并行设计多个模块"

## 选哪个 rtl 阶段 agent

当 spawn rtl 阶段时,主 Agent 按下面规则选:

1. 子模块是 CRG / clk_rst_gen / 时钟复位生成模块,**且**用户提供了 Excel 配置 → `soc-crg-engineer`
2. 当前任务是顶层集成(已有多个子模块 rtl=done) → `soc-integrator`
3. 其它(普通组合/时序/状态机) → `soc-rtl-designer`(默认)

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
8. 报告最终交付物路径

## 安全准则

- 执行任何可能破坏数据的命令前（`rm`, `git reset --hard`, `git push --force`, `git clean -f` 等），必须显式向用户确认并说明后果
- 执行 `python3` 脚本前，先检查脚本内容，确认没有破坏性操作（删除文件、覆盖系统配置、网络请求等）
- 不覆盖 `~/.ssh/`、`~/.zshrc`、`~/.bash_profile`、`/etc/` 等系统配置文件
- 编辑或写文件前，如果目标文件在 git 跟踪中，优先确认用户已保存当前工作
- 不主动执行 `sudo`、`chmod`、`chown` 等权限变更命令
- 不主动执行 `curl ... | bash` 或 `wget ...` 等远程脚本下载执行操作
- 使用 `cp`/`mv` 覆盖已有文件前，先确认目标文件不是关键配置或系统文件
- Agent 内部 spawn 的 subagent 同样遵循上述安全准则

---
*silicon-crew@siliconpeasant v1.0.0 — 2026-05-17*
