"""
基金持仓管理系统 - 统计视图功能
"""
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.database import Database
from src.models import FundHolding, FundInfo, FundHoldingsDetail, GroupColumn


class Statistics:
    """统计视图类"""

    def __init__(self, database: Database):
        self.database = database
        self.console = Console()

    def show_group_statistics(self, column: GroupColumn):
        """显示分组统计

        Args:
            column: 分组列名（GroupColumn 枚举）
        """
        data = self.database.get_group_statistics(column.value)

        if not data:
            self.console.print(f"[yellow]暂无{GroupColumn.get_display_name(column)}分布数据[/]")
            return

        display_name = GroupColumn.get_display_name(column)
        table = Table(title=f"{display_name}分布", show_header=True, header_style="bold cyan")
        table.add_column(display_name, style="cyan")
        table.add_column("持仓数", justify="right", style="blue")
        table.add_column("资产价值", justify="right", style="green")
        table.add_column("占比", justify="right", style="yellow")

        total = sum(item['total'] or 0 for item in data)

        for item in data:
            item_total = item['total'] or 0
            percentage = (item_total / total * 100) if total > 0 else 0
            table.add_row(
                str(item['name'] or "未知"),
                str(item['count']),
                f"¥{item_total:,.2f}",
                f"{percentage:.2f}%"
            )

        self.console.print(table)

    def show_query_result(self, column: GroupColumn, value: str):
        """显示查询结果

        Args:
            column: 查询列名（GroupColumn 枚举）
            value: 查询值
        """
        holdings = self.database.query_holdings(column.value, value)

        if not holdings:
            self.console.print(f"[yellow]未找到匹配 '{value}' 的持仓记录[/]")
            return

        display_name = GroupColumn.get_display_name(column)
        table = Table(title=f"查询结果: {display_name} 包含 '{value}' (共{len(holdings)}条)",
                      show_header=True, header_style="bold cyan")
        table.add_column("基金代码", style="cyan", width=10)
        table.add_column("基金名称", style="white", width=25)
        table.add_column("持有份额", justify="right", style="blue", width=12)
        table.add_column("净值", justify="right", style="yellow", width=8)
        table.add_column("资产价值", justify="right", style="green", width=12)
        table.add_column(display_name, style="magenta", width=18)

        # 根据查询列获取对应的显示值
        for holding in holdings[:50]:  # 限制显示50条
            col_value = self._get_column_value(holding, column)
            table.add_row(
                holding.fund_code,
                holding.fund_name[:25] if len(holding.fund_name) > 25 else holding.fund_name,
                f"{holding.holding_shares:,.2f}",
                f"{holding.nav:.4f}",
                f"¥{holding.asset_value:,.2f}",
                str(col_value)[:18] if col_value and len(str(col_value)) > 18 else str(col_value or "")
            )

        if len(holdings) > 50:
            self.console.print(f"[dim]... 还有 {len(holdings) - 50} 条记录未显示[/]")

        self.console.print(table)

        # 显示汇总信息
        total_value = sum(h.asset_value for h in holdings)
        self.console.print(f"\n[green]总计: {len(holdings)} 条记录, 资产价值: ¥{total_value:,.2f}[/]")

    def _get_column_value(self, holding: FundHolding, column: GroupColumn) -> Any:
        """获取持仓记录中指定列的值"""
        if column == GroupColumn.FUND_CODE:
            return holding.fund_code
        elif column == GroupColumn.FUND_NAME:
            return holding.fund_name
        elif column == GroupColumn.FUND_MANAGER:
            return holding.fund_manager
        elif column == GroupColumn.FUND_ACCOUNT:
            return holding.fund_account
        elif column == GroupColumn.TRADE_ACCOUNT:
            return holding.trade_account
        elif column == GroupColumn.SALES_AGENCY:
            return holding.sales_agency
        elif column == GroupColumn.CURRENCY:
            return holding.settlement_currency
        elif column == GroupColumn.DIVIDEND_METHOD:
            return holding.dividend_method
        elif column == GroupColumn.INVEST_TYPE:
            # 投资类型需要从 fund_info 获取
            fund_info = self.database.get_fund_info(holding.fund_code)
            return fund_info.fund_invest_type if fund_info else "未知"
        return None

    def show_fund_detail(self, fund_code: str):
        """显示单个基金的详细信息"""
        # 获取基础信息
        fund_info = self.database.get_fund_info(fund_code)
        # 获取持仓详情
        holdings_detail = self.database.get_fund_holdings_detail(fund_code)
        # 获取用户持仓
        user_holdings = []
        all_holdings = self.database.get_fund_holdings()
        for h in all_holdings:
            if h.fund_code == fund_code:
                user_holdings.append(h)

        if not fund_info and not user_holdings:
            self.console.print(f"[red]未找到基金: {fund_code}[/]")
            return

        # 显示基金基础信息
        if fund_info:
            info_text = f"""
[bold cyan]基金代码:[/] {fund_info.fund_code}
[bold cyan]基金名称:[/] {fund_info.fund_name}
[bold cyan]投资类型:[/] {fund_info.fund_invest_type or '未知'}
[bold cyan]风险等级:[/] {fund_info.risk_5_level or '未知'}
[bold cyan]最新净值:[/] {fund_info.nav or '未知'} ({fund_info.nav_date or '未知'})
[bold cyan]基金规模:[/] {fund_info.net_asset}亿 ({fund_info.fund_invest_type or ''})
[bold cyan]成立日期:[/] {fund_info.setup_date or '未知'}
"""
            if fund_info.yearly_roe:
                info_text += f"[bold cyan]七日年化:[/] {fund_info.yearly_roe}%\n"
            if fund_info.one_year_return:
                info_text += f"[bold cyan]近一年收益:[/] {fund_info.one_year_return}%\n"
            if fund_info.manager_names:
                info_text += f"[bold cyan]基金经理:[/] {fund_info.manager_names}\n"

            self.console.print(Panel(info_text, title="[bold green]基金基础信息[/]", border_style="green"))

        # 显示用户持仓
        if user_holdings:
            table = Table(title="我的持仓", show_header=True, header_style="bold cyan")
            table.add_column("基金账户", style="cyan")
            table.add_column("交易账户", style="blue")
            table.add_column("持有份额", justify="right", style="green")
            table.add_column("资产价值", justify="right", style="yellow")

            for h in user_holdings:
                table.add_row(
                    h.fund_account,
                    h.trade_account,
                    f"{h.holding_shares:,.2f}",
                    f"¥{h.asset_value:,.2f}"
                )

            self.console.print(table)

        # 显示持仓详情
        if holdings_detail:
            detail_text = f"\n[bold cyan]报告日期:[/] {holdings_detail.report_date or '未知'}\n"
            if holdings_detail.stock_invest_ratio:
                detail_text += f"[bold cyan]股票仓位:[/] {holdings_detail.stock_invest_ratio}%\n"
            if holdings_detail.bond_invest_ratio:
                detail_text += f"[bold cyan]债券仓位:[/] {holdings_detail.bond_invest_ratio}%\n"

            self.console.print(Panel(detail_text, title="[bold green]持仓分析[/]", border_style="green"))

            # 显示十大重仓股
            if holdings_detail.top_stocks:
                stock_table = Table(title="十大重仓股", show_header=True, header_style="bold cyan")
                stock_table.add_column("代码", style="cyan", width=12)
                stock_table.add_column("名称", style="white", width=20)
                stock_table.add_column("占比", justify="right", style="green")
                stock_table.add_column("金额(亿)", justify="right", style="yellow")

                for stock in holdings_detail.top_stocks[:10]:
                    stock_table.add_row(
                        stock.stock_code,
                        stock.stock_name,
                        f"{stock.holding_ratio}%" if stock.holding_ratio else "-",
                        f"{stock.holding_amount}" if stock.holding_amount else "-"
                    )

                self.console.print(stock_table)

            # 显示十大重仓债
            if holdings_detail.top_bonds:
                bond_table = Table(title="十大重仓债", show_header=True, header_style="bold cyan")
                bond_table.add_column("代码", style="cyan", width=12)
                bond_table.add_column("名称", style="white", width=20)
                bond_table.add_column("占比", justify="right", style="green")
                bond_table.add_column("金额(亿)", justify="right", style="yellow")

                for bond in holdings_detail.top_bonds[:10]:
                    bond_table.add_row(
                        bond.bond_code,
                        bond.bond_name,
                        f"{bond.holding_ratio}%" if bond.holding_ratio else "-",
                        f"{bond.holding_amount}" if bond.holding_amount else "-"
                    )

                self.console.print(bond_table)

    def show_all_stats(self):
        """显示所有统计视图"""
        stats = self.database.get_statistics()

        # 总览面板
        total_asset = stats['total_asset_value']
        fund_count = stats['fund_count']
        holding_count = stats['holding_count']

        overview_text = f"""
[bold cyan]总资产价值:[/] ¥{total_asset:,.2f}
[bold cyan]持仓基金数:[/] {fund_count} 只
[bold cyan]持仓记录数:[/] {holding_count} 条
[bold cyan]基金基础信息:[/] {stats['info_count']} 条
[bold cyan]基金持仓详情:[/] {stats['detail_count']} 条
"""
        self.console.print("\n" + "=" * 60 + "\n")
        self.console.print(Panel(overview_text, title="[bold green]投资组合总览[/]", border_style="green"))
        self.console.print()

        # 遍历所有分组列展示统计
        for column in GroupColumn:
            self.console.print()
            self.show_group_statistics(column)