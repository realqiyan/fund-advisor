# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fund-tools is a CLI-based fund portfolio management system (基金持仓管理系统) for managing fund holdings, importing CSV data, syncing with external MCP services, and displaying statistics.

## Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run CLI
python main.py --help
python main.py <command> [options]

# Common commands
python main.py init                    # Initialize environment (mcporter + qieman-mcp)
python main.py import-csv data/sample.csv  # Import holdings from CSV
python main.py holdings                # View holdings list
python main.py overview                # Show portfolio overview
python main.py sync --all              # Sync fund data from MCP service
python main.py stats                   # Show all statistics
python main.py detail 004137           # View specific fund detail
```

## Development Workflow

### Git Workflow

```bash
# Check status
git status

# Stage and commit changes
git add .
git commit -m "type: description"

# Push to GitHub
git push
```

### Commit Message Convention

Follow conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Example:
```
feat: 添加投资类型分布统计功能
fix: 修复CSV导入列名换行符问题
docs: 更新README安装说明
```

### Code Style

- Use Python 3.10+ features
- Follow PEP 8 naming conventions
- Use dataclasses for data models
- Use Click for CLI commands
- Use Rich for terminal output

## Architecture

```
main.py                 # CLI entry point (Click-based), all command definitions
src/
├── models.py           # Data models: FundHolding, FundInfo, FundHoldingsDetail, StockHolding, BondHolding
├── database.py         # SQLite operations, all CRUD methods, schema initialization
├── csv_importer.py     # CSV parsing and validation, Chinese column name mapping
├── mcp_service.py      # MCP integration via mcporter CLI, batch API calls
├── statistics.py       # Rich-based terminal output, reporting
└── env_checker.py      # Environment validation, mcporter/qieman-mcp setup
```

## Key Design Decisions

- **SQLite database** with three tables: `fund_holdings` (user holdings), `fund_info` (fund metadata), `fund_holdings_detail` (stock/bond holdings)
- **Composite primary key** for holdings: `(fund_account, trade_account, fund_code)`
- **Upsert pattern** throughout database operations for idempotent imports
- **Batch processing** in MCP service (max 20 funds per API call)
- **Multiple encoding support** for CSV import (utf-8, utf-8-sig, gbk, gb18030)

## External Dependencies

- **mcporter**: External CLI tool required for MCP service integration
- **qieman-mcp**: MCP server for fund data (configured in `~/.mcporter/mcporter.json`)

## CSV Import Format

Required columns (Chinese names):
- 基金代码, 基金名称, 基金账户, 交易账户, 持有份额, 份额日期, 基金净值, 净值日期, 资产情况（结算币种）

## Fund Types

Defined in `FundType` enum for future expansion: `PUBLIC_FUND`, `ETF`, `LOF`, `CLOSED_END`