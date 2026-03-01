# qieman-mcp 工具文档

## 概述

qieman-mcp 是基金投资工具包，提供基金、内容、投研、投顾等专业领域能力。

通过 mcporter CLI 调用：

```bash
mcporter call qieman-mcp.<tool_name> --args '<json_args>' --output json
```

## 工具列表

### BatchGetFundsDetail

批量获取基金详细信息

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| fundCodes | string[] | 是 | 基金代码数组，最多10个 |

**返回：**

```json
[
  {
    "fundCode": "004137",
    "data": {
      "summary": {
        "fundCode": "004137",
        "fundName": "华夏全球精选",
        "fundInvestType": "QDII",
        "risk5Level": 4,
        "nav": "1.234",
        "navDate": "2024年01月15日",
        "netAsset": "12.34亿",
        "setupDate": 1234567890000,
        "yearlyRoe": "2.34%",
        "oneYearReturn": "12.34%",
        "setupDayReturn": "123.45%"
      },
      "managers": [
        {
          "fundManagerName": "张三"
        }
      ],
      "assetPortfolios": [
        {"name": "股票", "ratio": "90.00%"},
        {"name": "债券", "ratio": "5.00%"},
        {"name": "现金", "ratio": "5.00%"}
      ]
    }
  }
]
```

**示例：**

```bash
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes": ["004137", "000001"]}' \
  --output json
```

### BatchGetFundsHolding

批量获取基金持仓情况

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| fundCodes | string[] | 是 | 基金代码数组，最多10个 |
| fundReportDate | int | 否 | 报告日期，格式如 20240630 |

**返回：**

```json
[
  {
    "fundCode": "004137",
    "data": {
      "fundCode": "004137",
      "reportDate": "2024年06月30日",
      "stockInvestRatio": "90.00%",
      "bondInvestRatio": "5.00%",
      "stockInvests": [
        {
          "code": "AAPL",
          "name": "苹果公司",
          "ratio": "5.00%",
          "amount": "0.50亿"
        }
      ],
      "bondInvests": [
        {
          "code": "123456",
          "name": "国债",
          "ratio": "2.00%",
          "amount": "0.20亿"
        }
      ]
    }
  }
]
```

**示例：**

```bash
mcporter call qieman-mcp.BatchGetFundsHolding \
  --args '{"fundCodes": ["004137"]}' \
  --output json
```

## 调用限制

- 单次最多查询 10 只基金
- 超过限制需分批处理