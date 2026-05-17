# silicon-agents

> 硅农 (Silicon Peasant) 的 Claude Code 智能体插件集合 · agent-driven 芯片设计流水线

`silicon-agents` 是 [@siliconpeasant](https://github.com/siliconpeasant) 的 Claude Code marketplace,装载所有以「智能体协作」方式驱动 SoC / IC 前端工程的插件。一个仓库,统一入口,持续扩展。

```
Marketplace: siliconpeasant
└── silicon-crew@siliconpeasant   ← SoC 前端 5 角色智能体集合
```

---

## 已发布插件

| Plugin | 版本 | 说明 |
|---|---|---|
| [`silicon-crew`](#silicon-crew) | v1.0.0 | 硅农工组 — SoC 前端 5 角色智能体流水线(doc → rtl → verify → syn → release) |

> 路线图(预留位):`silicon-bench`(验证 benchmark)、`silicon-tape`(流片打包专项)、`silicon-pdk`(PDK 助手)…

---

## 安装

### 方式 A:本地路径 marketplace(开发用)

在 `~/.claude/settings.json` 或项目 `.claude/settings.json` 加:

```jsonc
{
  "extraKnownMarketplaces": {
    "siliconpeasant": {
      "source": {
        "source": "directory",
        "path": "/path/to/silicon-agents"
      }
    }
  },
  "enabledPlugins": {
    "silicon-crew@siliconpeasant": true
  }
}
```

### 方式 B:从 GitHub 安装

```bash
claude plugin marketplace add github:siliconpeasant/silicon-agents
claude plugin install silicon-crew@siliconpeasant
```

---

## silicon-crew

SoC 前端设计 multi-agent 流水线。**主 Agent 编排,5 个 subagent 各司其职**:

| Subagent | 角色 | 触发 | 产物 |
|---|---|---|---|
| `soc-doc-engineer` | 文档工程师 | 用户提出新模块需求 | `docs/*.md` |
| `soc-rtl-designer` | RTL 设计 | doc 阶段完成 | `rtl/*.v` + `rtl/rtl.f` + `constraints/base.sdc` |
| `soc-verification-engineer` | 验证 | RTL 阶段完成 | `tb/*.v` + `sim/results/*.log` |
| `soc-synthesis-engineer` | 综合 | 仿真 PASS | `syn/output/netlist.v` + reports + `synthesis_report.md` |
| `soc-release-engineer` | 发布打包 | 综合 timing MET | `release/v1.0.0/` 完整包 |

### 工作流

```
用户需求 ("设计一个 mux2_1, 8-bit")
   ↓ 主 Agent
   ├─ spawn soc-doc-engineer          → docs/*.md
   ├─ spawn soc-rtl-designer          → rtl/*.v + rtl.f + base.sdc
   ├─ spawn soc-verification-engineer → tb/*.v + sim/results/*.log
   ├─ spawn soc-synthesis-engineer    → syn/netlist.v + reports
   └─ spawn soc-release-engineer      → release/v1.0.0/
```

### 内置 skill / MCP

- **`soc-build` skill + MCP server**:Verilog 端口提取、智能集成、wrapper 生成、filelist、lint、Excel/YAML → CRG / Memory Map / Regmap

### 依赖工具

- [`verilator`](https://www.veripool.org/verilator/) — lint
- [`iverilog`](https://github.com/steveicarus/iverilog) + `vvp` — 仿真
- [`yosys`](https://github.com/YosysHQ/yosys) — 综合
- `python3` ≥ 3.9 — MCP server 与 quality check 脚本

### Workspace 路径

所有 subagent 产物落在:
```
${CLAUDE_PLUGIN_ROOT}/workspace/<task_name>/
```

`<task_name>` 由用户指定或主 Agent 推导(小写下划线,如 `mux2_1`)。

---

## 仓库布局

```
silicon-agents/                          ← 仓库 = 市集
├── .claude-plugin/
│   └── marketplace.json                ← 市集元数据 (name = siliconpeasant)
├── silicon-crew/                       ← 插件 1
│   ├── .claude-plugin/plugin.json     ← 插件元数据
│   ├── .claude/CLAUDE.md              ← 主 Agent 编排规则
│   ├── agents/                        ← 5 个 subagent
│   ├── skills/soc-build/              ← Verilog 工具集 skill + MCP server
│   ├── hooks/                         ← SessionStart 注入规则
│   ├── rules/                         ← 强制规范 (lint/sim/syn 不许绕封装)
│   └── scripts/                       ← 每阶段 quality check 脚本
└── README.md                          ← 你正在看的这个
```

每个插件一个子目录,内部结构自洽。加新插件只需:
1. 在仓库根新增 `silicon-<name>/` 目录,放好 `.claude-plugin/plugin.json` + 内容
2. 在 `marketplace.json` 的 `plugins[]` 数组追加一项 `{ "name": "...", "source": "./silicon-<name>" }`

---

## 作者

**硅农 (Silicon Peasant)** — [@siliconpeasant](https://github.com/siliconpeasant)

> 在硅片上耕作。

---

## License

TBD
