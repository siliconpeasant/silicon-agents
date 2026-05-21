---
name: yml2reg
description: 从 YAML 寄存器描述生成 APB/AHB 接口的 Verilog regfile。
---

### 3.1 YAML → 寄存器 RTL — `yml2reg/yml2reg.py`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/yml2reg/scripts/yml2reg/yml2reg.py <reg.yml> <apb|ahb>
```

从 YAML 寄存器描述生成 APB/AHB 接口的 Verilog regfile。

**支持访问类型**：`rw`、`ro`、`wo`、`w1t`（写1置位）、`wc`（写1清零）

**输出**：`<NAME>_<PROTOCOL>_regfile.v`（输出到当前工作目录）

**YAML 格式示例**：
```yaml
name: my_reg
bytes: 4
offset: 0x000
registers:
  - name: ctrl_reg
    description: "control register"
    offset: 0x0
    fields:
      - { name: enable, lsb: 0, bits: 1, access: rw, reset: 0x0 }
```

被 `crg_gen.py` / `io_top_gen.py` / `excel_yml_gen.py` 内部自动调用。
