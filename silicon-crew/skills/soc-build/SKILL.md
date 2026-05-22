---
name: soc-build
description: SoC 项目脚手架与仿真基础 skill。提供项目初始化、模块创建、filelist 生成、lint 检查、编译仿真等核心能力。端口提取、顶层集成、CRG/寄存器生成等功能已拆分为独立 skill（soc-integrate、yml2reg、crg-req-to-design、cr-tree-diag-gen 等）。
---

# SoC Build

SoC 前端 RTL 集成与自动化生成专用 skill。

---

## 一、项目脚手架

### 1.1 项目初始化 — `soc_project_init.py`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-build/scripts/soc_project_init.py init <project_name> -o <output_dir> -t <top_module>
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-build/scripts/soc_project_init.py add_ip <ip_name> -p <project_dir> -t {digital|third_party}
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-build/scripts/soc_project_init.py add_chip <module_name> -p <project_dir>
```

生成标准化 SoC 前端目录结构：

```
<project_name>/
├── chip/                    # RTL 设计源码
│   ├── core/                # 子模块（目录结构与 IP 一致）
│   │   ├── de/rtl, de/run   # 设计 + 综合/ lint 输出
│   │   ├── dv/tb, dv/sim   # 验证 + 仿真输出
│   │   └── Makefile        # 模块级 Makefile
│   ├── bus/                 # 同上
│   ├── periph/              # 同上
│   ├── interconnect/        # 同上
│   ├── lib/                 # 同上
│   └── top/                 # 芯片级顶层（也是芯片级仿真入口）
│       ├── de/rtl/{top_module}.v
│       ├── de/rtl/filelist.mk
│       └── Makefile
├── ip/                      # IP 目录
│   ├── third_party/
│   └── digital/
│       └── template_ip/     # IP 模板（可独立仿真）
├── doc/                     # 文档
├── scripts/                 # 公共脚本（由 soc_project_init.py 自动生成指向 skill 的引用）
│   ├── setup.sh
│   └── common.mk
└── Makefile                 # 项目顶层入口
```

**设计原则**：
- 每个子模块（core/bus/periph/interconnect/lib/top）和 IP 的目录结构**完全一致**
- 设计（`de/`）和验证（`dv/`）分离
- **芯片级入口就是 `chip/top/`，没有全局的 `chip/Makefile` 或 `chip/run/**`

**自动生成文件**：
- `de/rtl/{module}.v` — RTL 模板（非空，含示例逻辑）
- `de/rtl/filelist.f` — 本模块 RTL 文件列表
- `de/rtl/filelist.mk` — 模块依赖声明（include guard + MODULE_FILELISTS 去重）
- `Makefile` — 模块级 Makefile
- `dv/tb/tb_{module}.sv` — Testbench 模板

### 1.2 共享编译规则 — `common.mk`

`/skills/soc-build/scripts/common.mk` 为各模块（IP / chip 子模块 / chip/top）的 Makefile 提供统一的仿真/编译规则。

**支持仿真器**：VCS、Verilator、Iverilog、Xcelium

```bash
cd chip/top      # 或 ip/digital/xxx
make flist       # 生成 de/rtl/filelist.f
make comp        # 编译仿真
make lint        # Lint 检查（默认 verilator）
make sim         # 运行仿真
make syn         # Yosys 综合（输出到 de/syn/）
```

**TOP_MODULE 自动切换**：
- 在 `de/` 或 `rtl/` 目录下执行 → 默认顶层为 **RTL 模块**（`{module_name}`）
- 在 `dv/` 或其他目录下执行 → 默认顶层为 **testbench**（`tb_{module_name}`）

**综合流程**（模块级 Makefile 内置）：

每个模块（IP / chip 子模块）的 Makefile 内置 `make syn` 目标，自动调用 Yosys：

```bash
cd chip/core
make syn          # 综合当前模块，RTL 来源自动从 filelist 获取
```

执行流程：
1. 收集 RTL 文件（含 filelist.mk 依赖链）
2. 自动生成 `de/syn/syn.ys` Yosys 脚本
3. 运行 `proc → flatten → opt → fsm → memory → techmap → opt`
4. 输出网表到 `de/syn/<module>_netlist.v`
5. 输出面积报告到 `de/syn/synth.log`

### 1.3 快速配置 — `setup.sh`

```bash
./setup.sh --install    # 安装依赖 + 自动写入 Kimi Code MCP 配置
./setup.sh              # 仅安装依赖，打印 MCP 配置（手动复制）
```

---

## 六、仿真与文件管理

### 6.1 Filelist 生成 — `soc_gen_flist.py`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/soc-build/scripts/soc_gen_flist.py <path> -o <filelist.f>
```

递归扫描目录，生成 `.f` 文件列表（legacy 工具，新项目推荐用 `make flist`）。

---

## 七、MCP Server

soc-build 同时提供轻量级 MCP Server，让 AI 助手直接通过工具调用执行常用操作。

### 7.1 快速配置

```bash
# 一键安装依赖 + 自动写入 Kimi Code MCP 配置
./setup.sh --install

# 或只安装依赖，手动复制配置
./setup.sh
```

### 7.2 手动启动

```bash
# stdio transport（本地 AI 助手使用）
python3 mcp_server.py

# SSE transport（HTTP，远程或 Web 端使用）
python3 mcp_server.py --sse
```

### 7.3 暴露的工具列表

| Tool | 功能 | 底层脚本 |
|------|------|----------|
| Tool | 功能 | 底层脚本 |
|------|------|----------|
| `soc_init` | 初始化 SoC 项目 | `soc_project_init.py init` |
| `soc_add_ip` | 新增 IP 模块 | `soc_project_init.py add_ip` |
| `soc_add_chip` | 新增 chip 子模块 | `soc_project_init.py add_chip` |
| `soc_flist` | 生成 filelist | `soc_gen_flist.py` |
| `soc_lint` | 执行 lint 检查 | `make lint` |
| `soc_comp` | 编译仿真 | `make comp` |

> 其他工具已拆分为独立 skill：
> - **soc-integrate**：`soc_extract`、`soc_instantiate`、`soc_integrate`、`soc_wrap`、`soc_csv`、`soc_snapshot`、`soc_diff`、`soc_extract_map`、`soc_update`、`soc_remove`
> - **yml2reg**：`yml2reg`
> - **excel-yml-gen**：`excel_yml_gen`
> - **crg-req-to-design**：`crg_req_to_design`
> - **cr-tree-diag-gen**：`cr_tree_diag_gen`
> - **crg-gen**（未注册）：`crg_gen`、`io_top_gen`、`gen_asic_memmap`、`gen_memwrap`

### 7.4 设计原则

- **核心 CLI 不动**：`${CLAUDE_PLUGIN_ROOT}/skills/soc-build/scripts/` 下的所有脚本保持原样，MCP Server 只是轻量包装层
- **全部功能暴露**：所有脚本均通过 MCP 可用，用户只需指定输入文件路径
- **统一错误处理**：所有 tool 返回字符串结果，stdout/stderr/exit code 统一捕获

### 7.5 配置示例（Kimi Code）

`setup.sh --install` 会自动写入，或手动在 `.kimi/mcp.json` 添加：

```json
{
  "mcpServers": {
    "soc-build": {
      "command": "python3",
      "args": ["/path/to/soc_build/mcp_server.py"]
    }
  }
}
```

---

## 八、CI 与测试

> `.github/workflows/ci.yml` 已移除。如需恢复 CI，建议按当前 skill 拆分后的结构重新设计测试矩阵（分别测试 `soc-build`、`soc-integrate`、`yml2reg` 等独立 skill）。

---

## 九、Verilog 代码审查

soc-build 支持基于公司编码规范的 Verilog 代码审查。审查时读取 `references/verilog_coding_style.md` 作为规范依据。

### 使用方式

用户可直接要求：

```
请用 soc-build 规范审查 chip/uart.v
请按 verilog 规范审查 xxx.v
```

### 审查流程

1. 读取 `references/verilog_coding_style.md` 中的规范条款
2. 读取用户指定的 `.v` / `.sv` 文件
3. 对照规范中的 **M(Mandatory)** / **S(Should)** / **R(Recommend)** 等级逐条检查
4. 输出结构化审查报告

### 输出格式

```markdown
## 审查报告：`<文件名>`

### [M] `<规则编号>` — `<规则简述>`
- **位置**：Line `<行号>` / `<信号或模块名>`
- **规范原文**："`<对应条款>`"
- **当前代码**：
  ```verilog
  <相关代码片段>
  ```
- **问题描述**：`<为什么违规>`
- **修正建议**：
  ```verilog
  <修正后的代码>
  ```

---
**统计**：`<M 级违规数>` 个 M，`<S 级违规数>` 个 S，`<R 级建议数>` 个 R  
**评分**：`<0-100>`/100  
**结论**：`<一句话总结>`
```

---

## 十、注意事项

1. **Python 依赖**
   - `pandas`、`numpy` — 所有 Excel 处理脚本需要
   - `xlrd` — `gen_memwrap.py` 需要（`pip install xlrd`）

2. **不要直接编辑生成的 top.v**
   - 文件头带有 `AUTO-GENERATED` 标记
   - 手动修改应通过 `extract-map` + `update` 流程保留

3. **信号命名**
   - 独有端口自动加模块前缀
   - 共享端口保持原名

4. **手动连线建议**
   - 修改顶层连线后运行 `extract-map` 提取到 JSON
   - 再 `update` 重新生成，确保变更被保留

5. **版本管理**
   - CI 自动化测试：`.github/workflows/ci.yml`

6. **Demo 模板位置**
   - 所有 Excel/YAML 参考模板统一放在 `references/` 目录
   - 脚本通过命令行参数接收路径，不会自动引用 `references/`
