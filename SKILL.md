---
name: fund-advisor
description: |
  基金投资咨询与持仓分析工具。提供基金信息查询、持仓管理、投资组合分析等功能。
  适用于用户询问基金相关信息、投资建议、持仓分析、基金数据查询等场景。
license: MIT
compatibility: 需要 mcporter CLI 和 qieman-mcp MCP 服务配置
metadata:
  author: fund-tools
  version: "1.0.0"
  mcp_servers: qieman-mcp
allowed-tools: Bash(mcporter:*) Bash(python:*) Read(*.csv) Write(*.csv)
---

# 基金顾投 Skill (fund-advisor)

整合 fund-tools 本地功能和 qieman-mcp MCP 服务，提供基金投资咨询和持仓分析能力。

## 触发场景

当用户需要：
- 查询基金信息（净值、经理、规模、持仓等）
- 管理和分析基金持仓
- 获取投资组合统计
- 导入/导出持仓数据
- 获取基金投资建议

## 核心功能

### 1. 基金投资咨询

直接通过 MCP 服务查询任意基金信息，无需本地数据库：

```bash
# 查询单只基金详情
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["004137"]}' --output json

# 批量查询多只基金
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["004137","000001","110022"]}' --output json

# 查询基金持仓明细
mcporter call qieman-mcp.BatchGetFundsHolding --args '{"fundCodes":["004137"]}' --output json
```

### 2. 持仓管理

管理用户的基金持仓数据：

```bash
# 初始化环境（检查 mcporter 和 qieman-mcp 配置）
scripts/fund-cli.sh init

# 导入 CSV 持仓文件
scripts/fund-cli.sh import-csv tools/data/holdings.csv

# 查看持仓列表
scripts/fund-cli.sh holdings

# 查看投资组合总览
scripts/fund-cli.sh overview
```

### 3. 数据同步

从 MCP 服务同步基金数据到本地数据库：

```bash
# 同步所有数据（基础信息 + 持仓详情）
scripts/fund-cli.sh sync --all

# 仅同步基金基础信息
scripts/fund-cli.sh sync --info

# 仅同步基金持仓详情
scripts/fund-cli.sh sync --detail
```

### 4. 持仓分析

```bash
# 查看基金详情
scripts/fund-cli.sh detail 004137

# 查看管理人分布
scripts/fund-cli.sh managers

# 查看销售机构分布
scripts/fund-cli.sh agencies

# 显示所有统计
scripts/fund-cli.sh stats

# 导出统计报告
scripts/fund-cli.sh export --output report.txt
```

## MCP 工具整合

通过 `mcporter` CLI 调用 `qieman-mcp` 服务：

### BatchGetFundsDetail

批量获取基金详细信息，包括：
- 基金名称、代码、类型
- 净值、净值日期
- 基金规模、成立日期
- 基金经理、风险等级
- 资产配置比例（股票/债券/现金）
- 收益率指标

### BatchGetFundsHolding

批量获取基金持仓详情，包括：
- 报告日期
- 股票投资比例
- 债券投资比例
- 十大重仓股
- 十大重仓债

详细参数和返回格式见 [references/mcp-tools.md](references/mcp-tools.md)

## 数据模型

### FundHolding - 用户持仓

| 字段 | 说明 |
|------|------|
| fund_code | 基金代码 |
| fund_name | 基金名称 |
| holding_shares | 持有份额 |
| nav | 净值 |
| asset_value | 资产市值 |

### FundInfo - 基金信息

| 字段 | 说明 |
|------|------|
| fund_code | 基金代码 |
| fund_name | 基金名称 |
| fund_invest_type | 投资类型 |
| risk_5_level | 风险等级(1-5) |
| net_asset | 基金规模(亿) |
| manager_names | 基金经理 |

详见 [references/reference.md](references/reference.md)

## CSV 导入格式

支持中文列名，必需字段：

- 基金代码, 基金名称, 基金账户, 交易账户
- 持有份额, 份额日期, 基金净值, 净值日期
- 资产情况（结算币种）

示例文件见 [assets/sample.csv](assets/sample.csv)

详细规范见 [references/csv-format.md](references/csv-format.md)

## 使用示例

### 示例1：查询基金信息

用户："帮我查一下易方达蓝筹精选的信息"

执行：
```bash
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["005827"]}' --output json
```

### 示例2：分析用户持仓

用户："分析一下我的基金持仓"

执行：
```bash
scripts/fund-cli.sh overview
scripts/fund-cli.sh stats
```

### 示例3：导入新持仓

用户："我有个CSV文件要导入"

执行：
```bash
scripts/fund-cli.sh import-csv /path/to/holdings.csv
```

### 示例4：同步最新数据

用户："更新一下基金数据"

执行：
```bash
scripts/fund-cli.sh sync --all
```

## 注意事项

1. **环境要求**：需要先运行 `init` 命令确保 mcporter 和 qieman-mcp 配置正确
2. **批量限制**：MCP 服务单次最多查询 10 只基金
3. **数据时效**：基金净值和持仓数据有延迟，注意查看净值日期
4. **CSV 编码**：支持 utf-8, utf-8-sig, gbk, gb18030 编码
5. **目录结构**：工程代码位于 `tools/` 目录下