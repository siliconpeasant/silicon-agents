# SoC RTL 编码规范

## 语言

- Verilog-2001 / Verilog-2005,**可综合**子集
- 不使用 `always_ff` / `always_comb` 等 SystemVerilog 关键字(除非项目明确要 SV)
- **严禁** latch 推断:`always @(*)` 块所有路径必须赋值,`if` 必有 `else` 或缺省值

## 复位

- **异步低有效复位** `rst_n`(下降沿生效或电平有效,项目约定)
- 所有时序逻辑 `always @(posedge clk or negedge rst_n)` 必须复位
- 纯组合模块无 `clk`/`rst_n`

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        q <= 1'b0;
    end else begin
        q <= d;
    end
end
```

## 参数

- 可配置参数用 `parameter`(实例化时可覆盖)
- 模块内派生常量用 `localparam`(不可覆盖)
- 参数名 UPPER_SNAKE_CASE

```verilog
module fifo #(
    parameter DEPTH = 16,
    parameter WIDTH = 32
)(
    ...
);
    localparam ADDR_W = $clog2(DEPTH);
endmodule
```

## 命名

- 模块名:`<func>_<role>` 或 `<prefix>_<func>`,下划线分隔,小写
- 文件名 = 模块名 + `.v`,**严格一致**
- 信号名 lower_snake_case
- 寄存器 `_q`,组合输出 `_n` 或 `_w`(项目约定)
- 时钟 `clk` 或 `<domain>_clk`,复位 `rst_n` 或 `<domain>_rst_n`

## 目录结构

| 路径 | 内容 |
|---|---|
| `<module>/de/rtl/` | 可综合 RTL `.v` |
| `<module>/de/rtl/<subcategory>/` | 子分类(如 `std_cell/`、`clk_gen/`) |
| `<module>/de/rtl/filelist.f` | RTL filelist,以 `$SOC` 起头的路径 |
| `<module>/dv/tb/` | testbench `.v`,文件名 `tb_<module>.v` |
| `<module>/dv/sim/` | 仿真产物(被 .gitignore) |
| `<module>/de/syn/` | 综合产物 + 约束 (`base.sdc`) |
| `<module>/de/run/` | lint/编译中间文件(被 .gitignore) |

## 文件头与注释

- 默认**不写**文件头注释,顶层模块除外
- 不写描述代码做什么的注释——好命名自带文档
- 只在 WHY 非显然时写注释:隐藏约束、特殊不变量、特殊 workaround
