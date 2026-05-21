---
name: excel-yml-gen
description: 从 Excel 寄存器描述生成 YAML 和 Verilog regfile。
---

### 3.2 Excel → YML/RTL — `excel_yml_gen.py`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/excel-yml-gen/scripts/excel_yml_gen.py <excel> <sheet_name> [output_dir]
```

从 Excel 寄存器描述生成 YAML 和 Verilog regfile。

**sheet 命名约定**：
- `<name>` — 主配置 sheet（component name / protocol / base address）
- `<name>_reg` — 寄存器定义 sheet
- `<name>_intp` — 中断定义 sheet（可选）

传入 `<name>_reg` 时脚本会自动去掉 `_reg` 后缀，读取三个 sheet。

**输出**：
- `<NAME>.yml` — 寄存器描述 YAML
- `<NAME>_apb_regfile.v` — 寄存器 RTL
- `<name>_reg_inst.v` — 实例化 wrapper
- `<name>_tdr_buf_list.txt`

Excel 模板：`references/excel2yml_demo.xlsx`
