---
name: soc-integrate
description: SoC 顶层集成与端口管理工具，支持 Verilog 端口提取、智能连接、顶层自动生成、端口变更追踪。
---

## 二、SoC 顶层集成

### 2.1 端口提取与实例化 — `soc_integrate.py`

| 子命令 | 功能 |
|--------|------|
| `extract` | 提取 Verilog 模块端口（方向、位宽、参数） |
| `instantiate` | 生成 `.port(signal)` 实例化代码 |
| `wrap` | 生成 wrapper 模块 |
| `csv` | 导出端口到 CSV |

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py extract <module.v> [-m <module_name>]
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py instantiate <module.v> [-n <instance_name>]
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py wrap <module.v> [-n <wrapper_name>]
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py csv <module.v> [-o <output.csv>]
```

### 2.2 顶层集成与刷新

| 子命令 | 功能 |
|--------|------|
| `integrate` | 集成多个模块到顶层（自动生成 `.integrate.json`） |
| `update` | 子模块端口变更后一键刷新顶层 |
| `remove` | 从集成配置中删除模块并自动刷新 |
| `extract-map` | 从顶层 `.v` 提取实例化连接关系 |

```bash
# 首次集成
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py integrate a.v b.v c.v -n soc_top -o soc_top.v

# 子模块端口更新后刷新
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py update soc_top.integrate.json

# 删除模块并刷新
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py remove soc_top.integrate.json dma

# 提取顶层连接关系
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py extract-map soc_top.v -o map.json
```

**智能连接规则**：

| 场景 | 处理结果 |
|------|----------|
| input + input (≥2 模块) | 顶层 input 端口（外部输入共享） |
| output + input (混合) | 内部 wire（output 驱动 input） |
| output + output | 各自独立，不共享 |
| 独有端口 | 加模块前缀作为独立顶层端口 |

**生成文件**：
- `soc_top.v` — 生成的顶层 RTL
- `soc_top.integrate.json` — 机器可读配置（模块路径、mappings、端口快照）
- `soc_top.integrate.csv` — 工程师 review 用

**变更标记**：
- `[NEW]` — 新增端口
- `[MOD]` — 方向/位宽修改
- `[DEL]` — 已删除端口

### 2.3 端口变更追踪

| 子命令 | 功能 |
|--------|------|
| `snapshot` | 保存端口快照（JSON + CSV） |
| `diff` | 对比当前端口与快照差异 |
| `check` | 检查端口是否符合规范 |

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py snapshot <module.v> -o <prefix>
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py diff <module.v> <snapshot.json>
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_integrate.py check <module.v> <spec.json>
```

### 2.4 CSV → RTL — `soc_build.py`

从 CSV 连接关系生成 Verilog 顶层模块。被 `crg_gen.py` / `io_top_gen.py` 内部自动调用。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-integrate/scripts/soc_build.py gen <top.csv>
```

---
