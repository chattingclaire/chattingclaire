# 数据源配置说明

本系统使用**多数据源架构**，针对不同市场和数据类型使用最优数据源。

## 📊 数据源架构

```
┌─────────────────────────────────────────────────┐
│           数据源分层架构                          │
└─────────────────────────────────────────────────┘

              ┌─────────────┐
              │   系统层    │
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼────┐  ┌───▼────┐
   │ Tushare │  │AKShare │  │ Yahoo  │
   │(A+港股) │  │(实时)  │  │(美股)  │
   └─────────┘  └────────┘  └────────┘
```

## 1️⃣ Tushare Pro（A股 + 港股）

### 🎯 主要用途
- **历史数据**（日线、周线、月线）
- **财务报表**（利润表、资产负债表、现金流量表）
- **财务指标**（ROE、ROA、毛利率等）
- **公司基本信息**
- **财报披露日期**

### 📌 配置信息
```bash
# .env
TUSHARE_TOKEN=924d36f94699aa84a6cd330084082d61257fe6d3b01a591527259e9a
```

### ✅ 优势
- 数据质量高，专业金融数据提供商
- 接口规范，字段标准化
- 历史数据完整
- 适合量化回测

### ⚠️ 限制
- 需要积分（免费版已足够基础使用）
- 部分高级接口需要更多积分
- 实时数据有延迟

### 🔧 使用示例
```python
from tools.datasources.tushare_tool import tushare_api, get_latest_financials

# 获取股票基本信息
info = tushare_api.get_stock_basic("600519.SH")

# 获取财务报表
financials = get_latest_financials("600519")
print(financials['income'])      # 利润表
print(financials['balance'])     # 资产负债表
print(financials['cashflow'])    # 现金流量表
print(financials['indicators'])  # 财务指标

# 获取日线行情
prices = tushare_api.get_daily_price(
    "600519.SH",
    start_date="20240101",
    end_date="20241231"
)
```

### 📊 支持的接口（免费可用）
| 接口 | 说明 | 权限 |
|------|------|------|
| `stock_basic` | 股票列表 | ✅ 免费 |
| `daily` | 日线行情 | ✅ 免费 |
| `income` | 利润表 | ✅ 免费 |
| `balancesheet` | 资产负债表 | ✅ 免费 |
| `cashflow` | 现金流量表 | ✅ 免费 |
| `fina_indicator` | 财务指标 | ✅ 免费 |
| `stock_company` | 公司信息 | ✅ 免费 |
| `disclosure_date` | 财报日期 | ✅ 免费 |

---

## 2️⃣ AKShare（实时数据 + 新闻）

### 🎯 主要用途
- **实时行情**（当前价、涨跌幅）
- **股票新闻**
- **公司公告**
- **资金流向**
- **热度排行**
- **千股千评**
- **市场情绪**

### 📌 配置信息
```bash
# 无需配置！完全免费
# AKShare 开源免费，无需 API Key
```

### ✅ 优势
- 完全免费，无需注册
- 实时数据（东方财富接口）
- 新闻公告即时更新
- 覆盖面广（A股、港股、美股、期货等）
- 社区活跃，更新频繁

### ⚠️ 限制
- 数据来源多样，格式可能不统一
- 部分接口稳定性依赖源网站
- 无官方技术支持

### 🔧 使用示例
```python
from tools.datasources.akshare_tool import akshare_api, get_stock_comprehensive_info

# 获取实时行情
realtime = akshare_api.get_realtime_quote("600519")
print(realtime['最新价'])
print(realtime['涨跌幅'])

# 获取股票新闻
news = akshare_api.get_stock_news("600519", limit=10)
for item in news:
    print(item['标题'], item['发布时间'])

# 获取公司公告
announcements = akshare_api.get_stock_announcements("600519")

# 获取资金流向
fund_flow = akshare_api.get_stock_fund_flow("600519")

# 获取市场热度排行
hot_stocks = akshare_api.get_stock_hot_rank()

# 获取综合信息（一次性获取所有）
info = get_stock_comprehensive_info("600519")
print(info['realtime'])      # 实时行情
print(info['news'])          # 新闻
print(info['announcements']) # 公告
print(info['fund_flow'])     # 资金流
```

### 📊 支持的功能
| 功能 | 说明 | 来源 |
|------|------|------|
| 实时行情 | 当前价、涨跌幅、成交量 | 东方财富 |
| 股票新闻 | 个股/市场新闻 | 东方财富 |
| 公司公告 | 上市公司公告 | 东方财富 |
| 资金流向 | 主力资金进出 | 东方财富 |
| 热度排行 | 股票人气榜 | 东方财富 |
| 千股千评 | 专业机构评论 | 东方财富 |
| 涨跌停统计 | 市场情绪指标 | 东方财富 |

---

## 3️⃣ Yahoo Finance（美股）

### 🎯 主要用途
- **美股实时行情**
- **美股财务数据**
- **美股公司信息**

### 📌 配置信息
```bash
# 无需配置！使用 yfinance 库
```

### 🔧 使用示例
```python
import yfinance as yf

# 获取美股信息
stock = yf.Ticker("AAPL")
info = stock.info

print(info['longName'])          # 公司名称
print(info['sector'])            # 行业
print(info['marketCap'])         # 市值
print(info['trailingPE'])        # PE 比率

# 获取历史数据
hist = stock.history(period="1mo")
```

---

## 🎯 数据源选择策略

系统根据**股票代码**自动选择最优数据源：

### A股（6位数字）
```python
ticker = "600519"  # 贵州茅台

# 使用策略：
历史数据 → Tushare      # 日线、周线、月线
财务数据 → Tushare      # 财报、指标
实时行情 → AKShare      # 当前价、涨跌幅
新闻公告 → AKShare      # 新闻、公告
```

### 港股（5位数字）
```python
ticker = "00700"  # 腾讯控股

# 使用策略：
历史数据 → Tushare      # .HK 后缀
财务数据 → Tushare
实时行情 → AKShare
```

### 美股（字母代码）
```python
ticker = "AAPL"  # 苹果

# 使用策略：
所有数据 → Yahoo Finance  # yfinance 库
```

---

## 📊 数据源对比

| 特性 | Tushare | AKShare | Yahoo Finance |
|------|---------|---------|---------------|
| **市场** | A股、港股 | A股、港股、美股 | 美股 |
| **费用** | 需Token（免费版可用） | 完全免费 | 完全免费 |
| **历史数据** | ✅ 优秀 | ✅ 良好 | ✅ 优秀 |
| **财务报表** | ✅ 完整 | ⚠️ 有限 | ✅ 完整 |
| **实时行情** | ⚠️ 有延迟 | ✅ 实时 | ✅ 实时 |
| **新闻公告** | ❌ 无 | ✅ 完整 | ⚠️ 有限 |
| **数据质量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **接口稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🔧 系统集成

### Fundamental Agent 数据获取流程

```python
def _analyze_ticker(ticker):
    # 1. 判断市场
    if is_chinese_stock(ticker):
        # A股/港股
        company_info = tushare_api.get_company_info(ticker)  # Tushare
        realtime = akshare_api.get_realtime_quote(ticker)    # AKShare
        financials = tushare_api.get_income_statement(ticker) # Tushare
        news = akshare_api.get_stock_news(ticker)            # AKShare
    else:
        # 美股
        stock = yf.Ticker(ticker)
        company_info = stock.info
        financials = stock.financials

    # 2. 合并数据
    return merge_data(company_info, realtime, financials, news)
```

---

## 🚀 最佳实践

### 1. 使用缓存减少 API 调用
```python
# 实时数据：缓存 1-5 分钟
# 日线数据：缓存 1 天
# 财务数据：缓存 1 季度
```

### 2. 错误处理和降级
```python
try:
    data = tushare_api.get_data(ticker)
except TushareException:
    # 降级到 AKShare
    data = akshare_api.get_data(ticker)
```

### 3. 批量请求优化
```python
# Tushare 支持批量查询
tickers = ["600519.SH", "000001.SZ", "600036.SH"]
batch_data = tushare_api.batch_query(tickers)
```

### 4. 监控 API 配额
```python
# Tushare 有积分限制
# 优先使用免费接口
# 监控每日调用次数
```

---

## 📝 配置检查清单

- [x] **Tushare Token**: 已配置 ✅
- [x] **AKShare**: 无需配置 ✅
- [x] **Yahoo Finance**: 无需配置 ✅

---

## 🆘 故障排查

### Tushare 常见问题

**问题 1：Token 无效**
```python
# 测试 Token
import tushare as ts
ts.set_token('YOUR_TOKEN')
pro = ts.pro_api()
df = pro.stock_basic()
print(df.head())
```

**问题 2：积分不足**
```python
# 检查积分
# 访问：https://tushare.pro/user/token
# 基础接口（日线、财报）免费可用
```

### AKShare 常见问题

**问题 1：接口返回空数据**
```python
# 可能是股票代码格式问题
# A股：去掉后缀（600519 而非 600519.SH）
# 港股：5位数字（00700 而非 700）
```

**问题 2：网络超时**
```python
# AKShare 访问国内网站，可能需要重试
import time
for retry in range(3):
    try:
        data = akshare_api.get_data(ticker)
        break
    except:
        time.sleep(2)
```

---

## 🎓 学习资源

- **Tushare 文档**: https://tushare.pro/document/2
- **AKShare 文档**: https://akshare.akfamily.xyz/
- **yfinance 文档**: https://pypi.org/project/yfinance/

---

**✅ 配置完成！** 系统已具备完整的多市场数据获取能力。
