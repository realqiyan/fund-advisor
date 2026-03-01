# Fund Tools - 基金持仓管理系统

一个 CLI 基金持仓管理工具，用于管理基金持仓、导入 CSV 数据、同步外部 MCP 服务数据并展示统计信息。

## 功能特性

- **CSV 数据导入**: 支持从 CSV 文件导入持仓数据，自动识别多种编码格式
- **数据同步**: 通过 MCP 服务同步基金基础信息和持仓详情
- **持仓管理**: 查看、统计和导出基金持仓数据
- **统计分析**: 投资组合总览、管理人分布、销售机构分布等多维度分析
- **Rich 终端输出**: 美观的表格和格式化输出

## 安装

### 前置要求

- Python 3.10+
- mcporter (用于 MCP 服务集成)
- qieman-mcp (MCP 服务，可选)

### 快速安装

```bash
# 克隆仓库
git clone <repository-url>
cd fund-advisor

# 使用脚本自动安装（首次运行时自动创建虚拟环境）
bash scripts/fund-cli.sh --help
```

### 手动安装

```bash
cd tools
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## 使用方法

### 基本命令

```bash
# 查看帮助
bash scripts/fund-cli.sh --help

# 或使用已安装的命令
source tools/venv/bin/activate
fund-tools --help
```

### 环境初始化

```bash
# 初始化环境（检查并配置 mcporter 和 qieman-mcp）
bash scripts/fund-cli.sh init

# 仅检查环境状态
bash scripts/fund-cli.sh init --check

# 强制重新配置
bash scripts/fund-cli.sh init --force
```

### 数据导入

```bash
# 从 CSV 文件导入持仓数据
bash scripts/fund-cli.sh import-csv tools/data/sample.csv

# 清空所有持仓记录
bash scripts/fund-cli.sh reset
```

### 持仓查看

```bash
# 查看持仓列表
bash scripts/fund-cli.sh holdings

# 按账户筛选
bash scripts/fund-cli.sh holdings --account "账户名"

# 查看基金详情
bash scripts/fund-cli.sh detail 004137

# 显示投资组合总览
bash scripts/fund-cli.sh overview
```

### 数据同步

```bash
# 同步基金基础信息
bash scripts/fund-cli.sh sync --info

# 同步基金持仓详情
bash scripts/fund-cli.sh sync --detail

# 同步所有信息
bash scripts/fund-cli.sh sync --all

# 指定批次大小（最大 10）
bash scripts/fund-cli.sh sync --all --batch-size 5
```

### 统计分析

```bash
# 显示所有统计视图
bash scripts/fund-cli.sh stats

# 显示基金管理人分布
bash scripts/fund-cli.sh managers

# 显示销售机构分布
bash scripts/fund-cli.sh agencies

# 显示投资类型分布
bash scripts/fund-cli.sh invest-type

# 导出统计报告
bash scripts/fund-cli.sh export --output report.txt
```

## CSV 导入格式

CSV 文件需包含以下列（支持中文列名）：

| 列名 | 说明 |
|------|------|
| 基金代码 | 基金的唯一标识代码 |
| 基金名称 | 基金全称 |
| 基金账户 | 基金账户标识 |
| 交易账户 | 交易账户标识 |
| 持有份额 | 持有的份额数量 |
| 份额日期 | 份额统计日期 |
| 基金净值 | 单位净值 |
| 净值日期 | 净值日期 |
| 资产情况（结算币种） | 资产金额及币种 |

支持的编码格式：`utf-8`、`utf-8-sig`、`gbk`、`gb18030`

## 项目结构

```
fund-advisor/
├── CLAUDE.md              # Claude Code 项目指南
├── scripts/
│   └── fund-cli.sh       # CLI 包装脚本
├── tools/                 # Python 包
│   ├── pyproject.toml    # 包配置
│   ├── requirements.txt  # 依赖列表
│   ├── venv/             # 虚拟环境（自动生成）
│   ├── data/             # 数据文件
│   └── src/              # 源代码
│       ├── cli.py        # CLI 入口 (Click)
│       ├── models.py     # 数据模型
│       ├── database.py   # SQLite 数据库操作
│       ├── csv_importer.py   # CSV 解析导入
│       ├── mcp_service.py    # MCP 服务集成
│       ├── statistics.py     # 统计输出 (Rich)
│       └── env_checker.py    # 环境检查
└── references/            # 参考文档
```

## 数据模型

### FundHolding - 基金持仓

记录用户的基金持有信息，使用联合主键 `(fund_account, trade_account, fund_code)` 标识唯一持仓。

### FundInfo - 基金信息

存储基金的基础元数据，包括净值、风险等级、投资类型等。

### FundHoldingsDetail - 持仓详情

记录基金的股票/债券持仓明细。

## 依赖

- **click**: CLI 框架
- **rich**: 终端美化输出
- **python-dateutil**: 日期处理

## 开发

```bash
# 进入开发环境
cd tools
source venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

## 许可证

MIT License

## 作者

qiyan <yhb3420@qq.com>