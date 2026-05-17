# Pipeline State 机制 (强制)

每个独立模块开发需求必须有一个 `pipeline_state.json`,作为**单一事实来源**(single source of truth)记录 5 阶段状态。

## 文件位置

放在**模块或 IP 包根目录**,例如:
- `ip/digital/timer/pipeline_state.json` (单模块)
- `ip/digital/soc_ip_common/pipeline_state.json` (多子模块 IP 包)
- `chip/core/pipeline_state.json`

禁止放在临时目录或 agent 私有目录。

## 两种模式

### 单模块模式 (默认)

一个 `pipeline_state.json` 管理一个模块的 5 阶段:
```bash
python3 init_state.py ./ip/digital/timer timer
```

### 多子模块模式 (IP 包)

一个 `pipeline_state.json` 管理一个 IP 目录下的多个独立子模块:
```bash
python3 init_state.py ./ip/digital/soc_ip_common \
  --submodules "clk_divider,std_cell_and,std_cell_mux,rst_synchronizer" \
  soc_ip_common
```

适用场景:
- `soc_ip_common` 这种包含 clk_gen / rst_gen / std_cell 多个子模块的 IP
- 每个子模块有独立的 rtl/tb/syn
- 整个目录用一个 state 文件统一把控

**更新时必须指定 `--module`**:
```bash
python3 update_state.py ./ip/digital/soc_ip_common --module rst_synchronizer rtl done \
  --artifacts "de/rtl/rst_gen/rst_synchronizer.v,..."
```

## 状态生命周期

### 创建

主 Agent 接到"设计 xxx 模块"需求后,**第一步**必须调用:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_state.py <module_dir> [module_name]
```

### 状态流转

```
pending → in_progress → done
              ↓
             fail
```

| 状态 | 含义 | 下游影响 |
|------|------|----------|
| `pending` | 等待启动 | 无 |
| `in_progress` | agent 正在工作 | 无 |
| `done` | 产物 + check 都 PASS | 解阻塞下游阶段 |
| `fail` | 产物或 check 不通过 | **阻塞整个流水线**,需修复后重试 |
| `blocked` | 上游依赖未完成 | 依赖全部 `done` 后自动变为 `pending` |

### 更新

每个 subagent **完成后必须**调用:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py <module_dir> <step> <status> [options]
```

**示例**:
```bash
# RTL 完成,lint clean
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py ./ip/digital/timer rtl done \
  --artifacts "de/rtl/timer.v,de/rtl/rtl.f,de/rtl/timer.sdc" \
  --check "lint:passed:verilator -Wall 0 warn 0 error"

# 验证失败
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py ./ip/digital/timer verif fail \
  --check "sim:failed:17 errors in TC-003" \
  --note "race condition at posedge clk, need #delay before check()"
```

### 查询

主 Agent 在 spawn 下一个 agent 前,**必须**先查询状态:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/query_state.py <module_dir>
```

根据输出决定:
- `next_actions` 为空 → 检查是否有 `fail`,有则报告用户;无则全部完成
- `next_actions` 有多个 → 按依赖顺序串行,无依赖的并行 spawn

## 各阶段依赖关系

```
doc ──→ rtl ──→ verif
          └────→ syn ──→ release
```

- `rtl` 依赖 `doc`
- `verif` 依赖 `rtl`
- `syn` 依赖 `rtl`
- `release` 依赖 `doc` + `rtl` + `verif` + `syn`

## Agent 强制步骤 (追加到各 agent 定义的末尾)

每个 subagent 在完成"自检"步骤后、"报告"步骤前,**必须**插入:

```
N. **更新 pipeline_state**:
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py <module_dir> <step> done \
     --artifacts "<相对路径1>,<相对路径2>" \
     --check "<tool>:passed:<备注>"
```

如果自检失败,更新为 `fail`:
```
N. **更新 pipeline_state**:
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py <module_dir> <step> fail \
     --check "<tool>:failed:<失败原因>" \
     --note "<修复建议>"
```

## 主 Agent 调度规范

1. **创建模块时**:先 `init_state.py`,再按 `next_actions` spawn agent
2. **agent 返回后**:先 `query_state.py` 确认状态,再决定下一步
3. **遇到 fail**:停止自动推进,向用户报告失败阶段 + 原因 + 建议
4. **禁止**:跳过 state 查询直接 spawn agent,或 agent 跳过 state 更新直接返回

## 已集成 state 更新的 agent 清单

| Agent | 阶段 | state 更新位置 |
|-------|------|---------------|
| soc-doc-engineer | doc | 自检 `check_doc_completeness` 之后 |
| soc-rtl-designer | rtl | 自检 `check_rtl_quality` + lint 之后 |
| soc-verification-engineer | verif | 自检 `check_sim_pass` 之后 |
| soc-synthesis-engineer | syn | 自检 `check_timing` 之后 |
| soc-release-engineer | release | 自检 `check_release_integrity` 之后 |
