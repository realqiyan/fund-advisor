---
name: fund-advisor
description: 基金投资顾问技能。提供个人持仓管理功能，并整合盈米且慢MCP服务，提供基金数据查询、投资组合分析、市场分析等服务。当用户询问基金投资、基金信息查询、财经信息查询、持仓分析等基金投资相关问题时激活此技能。
homepage: https://github.com/realqiyan/fund-advisor
metadata: {"clawdbot":{"emoji":"💰","requires":{"bins":["mcporter","python","pip"],"env":["QIEMAN_API_KEY"]}}}
compatibility: 需要 mcporter CLI 和 qieman-mcp MCP 服务配置
allowed-tools: Bash(mcporter:*) Bash(python:*) Bash(bash*) Read(*.csv) Read(*.md)
---

# 基金顾投 Skill (fund-advisor)

基金投资顾问技能。提供个人持仓管理功能，并整合盈米且慢MCP服务，提供基金数据查询、投资组合分析、市场分析等服务。

## 能力范围

1. 管理用户的基金持仓数据，用户导入数据时会创建 `./fund_portfolio.db` 数据文件，用于存储用户导入的数据，后续进行持仓数据分析。

2. 本技能整合且慢MCP的五大核心能力模块：

| 模块 | 能力说明 |
|------|----------|
| 金融数据 | 基金基础信息、净值历史、持仓明细、风险指标、业绩表现等 |
| 投研服务 | 基金筛选、基金诊断、回测分析、相关性分析、风险评估等 |
| 投顾服务 | 资产配置方案、投资规划、风险匹配、财务分析等 |
| 投顾内容 | 实时资讯解读、热点话题、基金经理观点、财经新闻等 |
| 通用服务 | 交易日查询、图表渲染、PDF生成、时间查询等 |

完整工具清单见 [references/mcp-tools-full.md](references/mcp-tools-full.md)

## 核心功能

### 1. 持仓管理

导入用户的持仓数据，后续进行数据分析使用。

```bash
# 初始化环境（检查 mcporter 和 qieman-mcp 配置）
scripts/fund-cli.sh init

# 查看持仓列表
scripts/fund-cli.sh holdings

# 查看投资组合总览
scripts/fund-cli.sh overview

# 导入 CSV 持仓文件 导入的数据会保持于 `./fund_portfolio.db` 数据文件中
scripts/fund-cli.sh import-csv tools/data/holdings.csv

# 同步所有数据到本地（基础信息 + 持仓详情）
scripts/fund-cli.sh sync --all

# 仅同步基金基础信息数据到本地
scripts/fund-cli.sh sync --info

# 仅同步基金持仓详情数据到本地
scripts/fund-cli.sh sync --detail
```

### 2. 持仓分析

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


### 3. 基金投资咨询

直接通过 MCP 服务查询任意基金信息，无需本地数据库：

```bash
# 查询单只基金详情
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["004137"]}' --output json

# 批量查询多只基金
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["004137","000001","110022"]}' --output json

# 查询基金持仓明细
mcporter call qieman-mcp.BatchGetFundsHolding --args '{"fundCodes":["004137"]}' --output json
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

- FundHolding - 用户持仓
- FundInfo - 基金信息

详见 [references/reference.md](references/reference.md)

## CSV 导入格式

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

## 高级功能场景

### 场景1：投资组合诊断分析

用户持有基金组合，需要诊断分析：

```bash
# 1. 查询基金信息
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes":["005094","320007","001003","040046"]}' \
  --output json

# 2. 基金相关性分析
mcporter call qieman-mcp.GetFundsCorrelation \
  --args '{"fundCodes":["005094","320007","001003","040046"]}' \
  --output json

# 3. 组合回测分析
mcporter call qieman-mcp.GetFundsBackTest \
  --args '{"fundCodes":["005094","320007","001003","040046"],"weights":[0.47,0.23,0.17,0.13]}' \
  --output json
```

### 场景2：资产配置方案规划

用户希望制定投资方案：

```bash
# 1. 获取资产配置方案
mcporter call qieman-mcp.GetAssetAllocationPlan \
  --args '{"expectedAnnualReturn":0.08}' \
  --output json

# 2. 蒙特卡洛模拟
mcporter call qieman-mcp.MonteCarloSimulate \
  --args '{"weights":[0.3,0.3,0.2,0.2],"years":3}' \
  --output json
```

### 场景3：基金筛选与对比

用户希望筛选符合特定条件的基金：

```bash
# 1. 基金搜索
mcporter call qieman-mcp.SearchFunds \
  --args '{"keyword":"红利","sortBy":"oneYearReturn","limit":10}' \
  --output json

# 2. 基金业绩对比
mcporter call qieman-mcp.GetBatchFundPerformance \
  --args '{"fundCodes":["005827","000001","110022"]}' \
  --output json

# 3. 基金诊断
mcporter call qieman-mcp.GetFundDiagnosis \
  --args '{"fundCode":"005827"}' \
  --output json
```

### 场景4：市场分析

用户希望了解市场情况：

```bash
# 1. 市场温度计
mcporter call qieman-mcp.GetLatestQuotations \
  --args '{"date":"2025-03-01"}' \
  --output json

# 2. 热点话题
mcporter call qieman-mcp.SearchHotTopic \
  --args '{"limit":10}' \
  --output json

# 3. 基金经理观点
mcporter call qieman-mcp.SearchManagerViewpoint \
  --args '{"industry":"科技","limit":5}' \
  --output json
```

## 报告生成

支持生成可视化报告：

```bash
# ECharts图表渲染
mcporter call qieman-mcp.RenderEchart \
  --args '{"option":{...}}' \
  --output json

# HTML转PDF
mcporter call qieman-mcp.RenderHtmlToPdf \
  --args '{"html":"..."}' \
  --output json
```

## 环境配置

### 1. 配置环境变量

设置 `QIEMAN_API_KEY` 环境变量：

```bash
# 临时设置（当前终端会话）
export QIEMAN_API_KEY="your-api-key-here"

# 永久设置（添加到 shell 配置文件）
echo 'export QIEMAN_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

获取 API Key：访问 [且慢MCP官网](https://qieman.com/mcp/account) 申请免费 API Key。

### 2. 安装 mcporter

```bash
# NPM
npm install -g mcporter

# 或 Homebrew
brew tap steipete/tap
brew install mcporter
```

### 3. 初始化环境

```bash
# 检查并初始化环境（会自动使用环境变量中的 API Key 配置 qieman-mcp）
scripts/fund-cli.sh init
```

初始化脚本会：
1. 检查 mcporter 是否已安装
2. 检查 `QIEMAN_API_KEY` 环境变量是否已配置
3. 自动生成 `~/.mcporter/mcporter.json` 配置文件
4. 测试 MCP 服务连接

## 参考文档

- [MCP工具完整清单](references/mcp-tools-full.md)
- [MCP工具基础文档](references/mcp-tools.md)
- [CSV导入格式规范](references/csv-format.md)
- [项目架构说明](references/REFERENCE.md)
