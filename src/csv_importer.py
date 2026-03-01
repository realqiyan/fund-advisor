"""
基金持仓管理系统 - CSV导入功能
"""
import csv
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

from src.models import FundHolding, FundType
from src.database import Database


class CSVImporter:
    """CSV导入器"""

    # CSV列名映射
    COLUMN_MAPPING = {
        "基金代码": "fund_code",
        "基金名称": "fund_name",
        "份额类别": "share_class",
        "基金管理人": "fund_manager",
        "基金账户": "fund_account",
        "销售机构": "sales_agency",
        "交易账户": "trade_account",
        "持有份额": "holding_shares",
        "份额日期": "share_date",
        "基金净值": "nav",
        "净值日期": "nav_date",
        "资产情况 （结算币种）": "asset_value",
        "结算币种": "settlement_currency",
        "分红方式": "dividend_method"
    }

    def __init__(self, database: Database):
        self.database = database

    def import_from_csv(self, csv_path: str, encoding: str = "utf-8") -> Tuple[int, int, List[str]]:
        """
        从CSV文件导入基金持有信息

        Args:
            csv_path: CSV文件路径
            encoding: 文件编码，默认utf-8

        Returns:
            (成功数量, 失败数量, 错误信息列表)
        """
        success_count = 0
        fail_count = 0
        errors = []

        csv_file = Path(csv_path)
        if not csv_file.exists():
            return 0, 0, [f"文件不存在: {csv_path}"]

        # 尝试多种编码
        encodings = [encoding, "utf-8-sig", "gbk", "gb18030"]

        for enc in encodings:
            try:
                with open(csv_file, "r", encoding=enc) as f:
                    # 读取第一行检测编码
                    first_line = f.readline()
                    f.seek(0)

                    reader = csv.DictReader(f)
                    rows = list(reader)

                    if rows:
                        encoding = enc
                        break
            except UnicodeDecodeError:
                continue
        else:
            return 0, 0, [f"无法识别文件编码: {csv_path}"]

        # 导入数据
        try:
            with open(csv_file, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是标题）
                    try:
                        holding = self._parse_row(row, row_num)
                        if holding:
                            self.database.upsert_fund_holding(holding)
                            success_count += 1
                    except Exception as e:
                        fail_count += 1
                        errors.append(f"第{row_num}行: {str(e)}")
        except Exception as e:
            return 0, 0, [f"读取文件失败: {str(e)}"]

        return success_count, fail_count, errors

    def _parse_row(self, row: dict, row_num: int) -> Optional[FundHolding]:
        """解析CSV行数据"""
        # 映射列名
        mapped_row = {}
        for csv_col, model_col in self.COLUMN_MAPPING.items():
            value = row.get(csv_col, "").strip()
            if not value:
                # 尝试其他可能的列名
                for key in row.keys():
                    if csv_col in key or key in csv_col:
                        value = row.get(key, "").strip()
                        break
            mapped_row[model_col] = value

        # 验证必填字段
        required_fields = ["fund_code", "fund_name", "fund_account", "trade_account",
                          "holding_shares", "share_date", "nav", "nav_date", "asset_value"]

        for field in required_fields:
            if not mapped_row.get(field):
                raise ValueError(f"缺少必填字段: {field}")

        # 解析数值字段
        try:
            holding_shares = float(mapped_row["holding_shares"].replace(",", ""))
        except ValueError:
            raise ValueError(f"无效的持有份额: {mapped_row['holding_shares']}")

        try:
            nav = float(mapped_row["nav"])
        except ValueError:
            raise ValueError(f"无效的基金净值: {mapped_row['nav']}")

        try:
            asset_value = float(mapped_row["asset_value"].replace(",", ""))
        except ValueError:
            raise ValueError(f"无效的资产情况: {mapped_row['asset_value']}")

        # 解析日期字段
        share_date = self._parse_date(mapped_row["share_date"])
        if not share_date:
            raise ValueError(f"无效的份额日期: {mapped_row['share_date']}")

        nav_date = self._parse_date(mapped_row["nav_date"])
        if not nav_date:
            raise ValueError(f"无效的净值日期: {mapped_row['nav_date']}")

        return FundHolding(
            fund_code=mapped_row["fund_code"],
            fund_name=mapped_row["fund_name"],
            share_class=mapped_row.get("share_class", ""),
            fund_manager=mapped_row.get("fund_manager", ""),
            fund_account=mapped_row["fund_account"],
            sales_agency=mapped_row.get("sales_agency", ""),
            trade_account=mapped_row["trade_account"],
            holding_shares=holding_shares,
            share_date=share_date,
            nav=nav,
            nav_date=nav_date,
            asset_value=asset_value,
            settlement_currency=mapped_row.get("settlement_currency", "人民币"),
            dividend_method=mapped_row.get("dividend_method", ""),
            fund_type=FundType.PUBLIC_FUND
        )

    def _parse_date(self, date_str: str) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None

        date_str = date_str.strip()

        # 尝试多种日期格式
        formats = [
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%Y.%m.%d",
            "%Y年%m月%d日"
        ]

        for fmt in formats:
            try:
                return date.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def validate_csv(self, csv_path: str) -> Tuple[bool, List[str]]:
        """
        验证CSV文件格式

        Args:
            csv_path: CSV文件路径

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        csv_file = Path(csv_path)

        if not csv_file.exists():
            return False, [f"文件不存在: {csv_path}"]

        if not csv_file.suffix.lower() == ".csv":
            return False, [f"不是CSV文件: {csv_path}"]

        # 检查必需的列
        required_columns = ["基金代码", "基金名称", "基金账户", "交易账户",
                           "持有份额", "份额日期", "基金净值", "净值日期"]

        # 尝试读取文件
        encodings = ["utf-8", "utf-8-sig", "gbk", "gb18030"]

        for encoding in encodings:
            try:
                with open(csv_file, "r", encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or []

                    missing_columns = []
                    for col in required_columns:
                        found = False
                        for h in headers:
                            if col in h or h in col:
                                found = True
                                break
                        if not found:
                            missing_columns.append(col)

                    if missing_columns:
                        errors.append(f"缺少必需列: {', '.join(missing_columns)}")
                        return False, errors

                    return True, []
            except UnicodeDecodeError:
                continue
            except Exception as e:
                errors.append(f"读取文件失败: {str(e)}")
                return False, errors

        return False, [f"无法识别文件编码: {csv_path}"]