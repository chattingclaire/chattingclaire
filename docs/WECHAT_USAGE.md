# 微信消息输入使用指南

完整教程：如何把微信群聊消息导入到交易系统中。

---

## 📱 第一步：导出微信消息

### 方法1：手动复制粘贴（最简单）

#### 1.1 在手机上复制消息

1. 打开微信群聊
2. 长按消息选择"复制"
3. 复制多条关于股票讨论的消息

#### 1.2 创建TXT文件

创建文件 `my_wechat_messages.txt`，格式如下：

```text
[2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了，看好后续表现
[2025-01-15 10:35:00] 李四: 600519目标价2800，基本面持续向好
[2025-01-15 11:00:00] 王五: 茅台Q4业绩超预期，建议关注
[2025-01-15 14:30:00] 赵六: 五粮液也不错，可以考虑配置
[2025-01-15 15:00:00] 孙七: 白酒板块整体估值合理，长期看好
```

**格式要求**：
- 时间格式：`[YYYY-MM-DD HH:MM:SS]`
- 发送者和内容用 `:` 或 `：` 分隔
- 每条消息一行

### 方法2：导出为JSON（推荐）

#### 2.1 创建JSON文件

创建文件 `my_wechat_messages.json`：

```json
[
  {
    "sender": "张三",
    "content": "贵州茅台今天涨停了，看好后续表现",
    "timestamp": "2025-01-15T10:30:00",
    "chat_name": "股票交流群"
  },
  {
    "sender": "李四",
    "content": "600519目标价2800，基本面持续向好",
    "timestamp": "2025-01-15T10:35:00",
    "chat_name": "股票交流群"
  },
  {
    "sender": "王五",
    "content": "茅台Q4业绩超预期，建议关注",
    "timestamp": "2025-01-15T11:00:00",
    "chat_name": "股票交流群"
  }
]
```

**字段说明**：
- `sender`：发送者昵称（必需）
- `content`：消息内容（必需）
- `timestamp`：时间戳（可选，格式：ISO 8601）
- `chat_name`：群名称（可选）
- `message_type`：消息类型（可选：text, image, link）

### 方法3：导出为CSV

创建文件 `my_wechat_messages.csv`：

```csv
sender,content,timestamp,chat_name
张三,贵州茅台今天涨停了，看好后续表现,2025-01-15T10:30:00,股票交流群
李四,600519目标价2800，基本面持续向好,2025-01-15T10:35:00,股票交流群
王五,茅台Q4业绩超预期，建议关注,2025-01-15T11:00:00,股票交流群
```

### 方法4：使用第三方导出工具

推荐工具：
- **WeChatMsg**：支持导出数据库格式
- **WechatExporter**：可以导出HTML和文本格式
- **微信PC版**：可以批量导出聊天记录

---

## 💻 第二步：将消息导入系统

### 方式A：使用Python API（推荐）

#### A.1 基础使用

```python
from orchestrator import TradingOrchestrator

# 创建orchestrator
orchestrator = TradingOrchestrator()

# 运行完整pipeline
results = await orchestrator.run_pipeline(
    wechat_export_path="data/wechat/my_wechat_messages.txt",
    mode="full"
)

print(f"处理了 {results['agent_results']['wx_source']['processed_messages']} 条消息")
print(f"生成了 {len(results['stock_picks'])} 个股票推荐")
```

#### A.2 只处理微信数据（不执行交易）

```python
from agents.wx_source import WxSourceAgent

# 创建agent
wx_agent = WxSourceAgent()

# 处理微信导出
results = wx_agent.run(
    wechat_export_path="data/wechat/my_wechat_messages.json",
    export_type="json",  # auto, json, csv, txt
    process_images=False,  # 是否处理图片OCR
    process_links=False    # 是否抓取链接文章
)

print(f"✓ 处理了 {results['processed_messages']} 条消息")
print(f"✓ 成功率: {results['success_rate']:.1%}")
```

#### A.3 批量处理多个文件

```python
import os
from pathlib import Path

# 处理目录中的所有文件
wechat_dir = Path("data/wechat/exports")

for file_path in wechat_dir.glob("*.json"):
    print(f"处理文件: {file_path.name}")

    results = wx_agent.run(
        wechat_export_path=str(file_path),
        export_type="auto"  # 自动检测格式
    )

    print(f"  ✓ {results['processed_messages']} 条消息")
```

### 方式B：使用Memory API直接索引

如果你只想索引消息用于语义搜索（不运行交易流程）：

```python
from memory.enhanced_context import get_enhanced_context_manager

# 获取context manager
ctx = get_enhanced_context_manager()

# 准备消息数据
messages = [
    {
        "message_id": "msg_001",
        "content": "贵州茅台今天涨停了，看好后续表现",
        "sender": "张三",
        "timestamp": "2025-01-15T10:30:00",
        "chat_id": "group_123"
    },
    {
        "message_id": "msg_002",
        "content": "600519目标价2800，基本面持续向好",
        "sender": "李四",
        "timestamp": "2025-01-15T10:35:00",
        "chat_id": "group_123"
    }
]

# 批量索引
indexed_count = ctx.index_wechat_messages(
    messages=messages,
    batch_size=100
)

print(f"✓ 已索引 {indexed_count} 条消息")

# 现在可以搜索了
results = ctx.search_similar_content(
    query="贵州茅台",
    source_filter="wx_raw_messages",
    limit=10,
    threshold=0.7
)

print(f"找到 {len(results)} 条相关消息")
```

### 方式C：使用REST API

如果API服务器正在运行（`./start_api.sh`）：

```bash
# 索引微信消息
curl -X POST "http://localhost:8000/api/search/index/wechat" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "message_id": "msg_001",
        "content": "贵州茅台今天涨停了",
        "sender": "张三",
        "timestamp": "2025-01-15T10:30:00",
        "chat_id": "group_123"
      },
      {
        "message_id": "msg_002",
        "content": "600519目标价2800",
        "sender": "李四",
        "timestamp": "2025-01-15T10:35:00",
        "chat_id": "group_123"
      }
    ],
    "source_table": "wx_raw_messages",
    "batch_size": 100
  }'

# 搜索微信消息
curl -X POST "http://localhost:8000/api/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "贵州茅台",
    "source_filter": "wx_raw_messages",
    "limit": 10,
    "threshold": 0.7
  }'
```

---

## 🔄 第三步：运行完整交易流程

### 3.1 运行完整Pipeline

```python
import asyncio
from orchestrator import TradingOrchestrator

async def main():
    # 创建orchestrator
    orchestrator = TradingOrchestrator(config={
        "initial_capital": 100000,  # 初始资金10万
    })

    # 运行完整6-agent流程
    results = await orchestrator.run_pipeline(
        wechat_export_path="data/wechat/my_wechat_messages.json",
        mode="full"
    )

    # 查看结果
    print("=" * 60)
    print("处理结果")
    print("=" * 60)

    # 微信信号
    wx_stats = results['agent_results']['wx_source']
    print(f"✓ 微信消息: {wx_stats['processed_messages']} 条")

    # 外部信号
    ext_stats = results['agent_results']['external_source']
    print(f"✓ 外部信号: {ext_stats['total_items']} 条")

    # 股票选择
    picks = results['stock_picks']
    print(f"✓ 股票推荐: {len(picks)} 只")

    for pick in picks[:5]:  # 显示前5个
        print(f"  - {pick['ticker']}: {pick['action']} "
              f"(置信度 {pick['confidence']:.1%}, "
              f"微信权重 {pick['wx_weight']:.1%})")

    # 交易执行
    trades = results.get('trades', [])
    print(f"✓ 执行交易: {len(trades)} 笔")

    for trade in trades:
        print(f"  - {trade['ticker']}: {trade['action']} "
              f"{trade['quantity']} 股 @ ¥{trade['price']:.2f}")

# 运行
asyncio.run(main())
```

### 3.2 只运行信号收集（不执行交易）

```python
# 只收集和分析信号，不执行交易
results = await orchestrator.run_pipeline(
    wechat_export_path="data/wechat/my_wechat_messages.json",
    mode="signals_only"  # 只运行前3个agent
)
```

---

## 📊 第四步：查看和分析结果

### 4.1 查看股票推荐

```python
# 获取所有股票推荐
from database.supabase_client import get_supabase_client

db = get_supabase_client()

# 查询最近的推荐
picks = db.table("stock_picks")\
    .select("*")\
    .order("created_at", desc=True)\
    .limit(20)\
    .execute()

for pick in picks.data:
    print(f"{pick['ticker']}: {pick['action']} "
          f"- 微信权重 {pick['wx_weight']:.1%}")
    print(f"  原因: {', '.join(pick['reasons'][:3])}")
    print(f"  证据: {pick['wx_evidence'][:100]}...")
    print()
```

### 4.2 使用Search API查询

```python
from memory.enhanced_context import get_enhanced_context_manager

ctx = get_enhanced_context_manager()

# 获取某只股票的完整上下文
context = ctx.get_ticker_context(
    ticker="600519",
    include_history=True,
    days_back=30
)

print(f"贵州茅台 (600519) 上下文：")
print(f"  - 微信讨论: {len(context['wx_signals'])} 条")
print(f"  - 外部信号: {len(context['external_signals'])} 条")
print(f"  - 历史推荐: {len(context['picks'])} 次")

# 查看微信讨论内容
for signal in context['wx_signals'][:5]:
    print(f"\n[{signal['sender']}]: {signal['content'][:100]}")
```

---

## ⚙️ 高级配置

### 配置1：调整微信权重

在 `config/agents.yaml` 中修改：

```yaml
selection_agent:
  min_wx_weight: 0.60  # 微信权重最低60%（可调整到0.7, 0.8）
  min_confidence: 0.6  # 最低置信度阈值
```

### 配置2：只使用微信信号

```python
# 只用微信信号，不使用外部数据
results = await orchestrator.run_pipeline(
    wechat_export_path="data/wechat/messages.json",
    mode="full"
)

# 在SelectionAgent中会自动生成两种推荐：
# 1. 100% 微信信号（wx_only模式）
# 2. 60-100% 微信 + 0-40% 外部（hybrid模式）
```

### 配置3：处理图片和链接

```python
# 启用OCR处理图片中的文字
results = wx_agent.run(
    wechat_export_path="data/wechat/messages.json",
    process_images=True,  # 提取图片中的文字
    process_links=True    # 抓取微信公众号文章内容
)
```

---

## 📂 文件组织建议

```
chattingclaire/
└── data/
    └── wechat/
        ├── exports/              # 原始导出文件
        │   ├── group_1.txt
        │   ├── group_2.json
        │   └── group_3.csv
        ├── processed/            # 处理后的数据
        └── archives/             # 历史归档
            ├── 2025-01/
            └── 2025-02/
```

---

## 🔍 示例：完整工作流

### 示例1：日常使用流程

```python
#!/usr/bin/env python3
"""每日股票信号处理脚本"""

import asyncio
from datetime import datetime
from orchestrator import TradingOrchestrator

async def daily_pipeline():
    # 1. 准备今天的微信数据
    today = datetime.now().strftime("%Y-%m-%d")
    wechat_file = f"data/wechat/exports/messages_{today}.json"

    print(f"处理日期: {today}")
    print(f"数据文件: {wechat_file}")

    # 2. 运行pipeline
    orchestrator = TradingOrchestrator()

    results = await orchestrator.run_pipeline(
        wechat_export_path=wechat_file,
        mode="signals_only"  # 先只生成信号，不执行交易
    )

    # 3. 查看推荐
    picks = results['stock_picks']
    print(f"\n今日推荐 {len(picks)} 只股票：\n")

    for i, pick in enumerate(picks, 1):
        print(f"{i}. {pick['ticker']} - {pick['action']}")
        print(f"   置信度: {pick['confidence']:.1%}")
        print(f"   微信权重: {pick['wx_weight']:.1%}")
        print(f"   目标价: ¥{pick['target_price']}")
        print(f"   原因: {', '.join(pick['reasons'][:2])}")
        print()

    # 4. 等待人工确认后执行交易
    confirm = input("是否执行交易？(y/n): ")
    if confirm.lower() == 'y':
        # 执行交易
        trade_results = await orchestrator.execute_trades(picks)
        print(f"\n✓ 已执行 {len(trade_results)} 笔交易")

if __name__ == "__main__":
    asyncio.run(daily_pipeline())
```

### 示例2：回测历史数据

```python
"""回测历史微信数据"""

import asyncio
from pathlib import Path
from orchestrator import TradingOrchestrator

async def backtest_historical_data():
    # 获取所有历史文件
    wechat_dir = Path("data/wechat/archives/2024-12")
    files = sorted(wechat_dir.glob("*.json"))

    orchestrator = TradingOrchestrator(config={
        "initial_capital": 100000,
        "paper_trading": True  # 模拟交易
    })

    all_picks = []

    for file_path in files:
        print(f"处理: {file_path.name}")

        results = await orchestrator.run_pipeline(
            wechat_export_path=str(file_path),
            mode="full"
        )

        picks = results['stock_picks']
        all_picks.extend(picks)

        print(f"  推荐: {len(picks)} 只")

    # 分析统计
    print(f"\n总共推荐: {len(all_picks)} 只股票")

    # 按ticker统计
    ticker_counts = {}
    for pick in all_picks:
        ticker = pick['ticker']
        ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

    print("\n最常推荐的股票：")
    for ticker, count in sorted(ticker_counts.items(),
                                key=lambda x: x[1],
                                reverse=True)[:10]:
        print(f"  {ticker}: {count} 次")

asyncio.run(backtest_historical_data())
```

---

## ❓ 常见问题

### Q1: 支持哪些消息格式？

**A**: 支持以下格式：
- ✅ JSON（推荐）
- ✅ CSV
- ✅ TXT（需要规范格式）
- ✅ 目录（包含多个文件）

### Q2: 时间格式要求？

**A**: 支持多种格式：
- `2025-01-15T10:30:00` (ISO 8601)
- `2025-01-15 10:30:00`
- `2025/01/15 10:30:00`
- Unix时间戳

### Q3: 必需字段有哪些？

**A**: 最少需要：
- `content` 或 `message` - 消息内容
- `sender` 或 `from` - 发送者（可选，默认"Unknown"）

其他字段都会自动生成默认值。

### Q4: 如何提高识别准确率？

**A**: 建议：
1. 消息内容包含股票代码（如600519）
2. 提供时间戳
3. 消息长度适中（不要太短）
4. 包含明确的观点（看好/看空）

### Q5: 数据会保存在哪里？

**A**:
- **原始消息**: Supabase表 `wx_raw_messages`
- **向量嵌入**: Supabase表 `embeddings`
- **股票推荐**: Supabase表 `stock_picks`
- **交易记录**: Supabase表 `trades`

### Q6: 如何删除已索引的数据？

**A**:
```python
from database.supabase_client import get_supabase_client

db = get_supabase_client()

# 删除特定日期的消息
db.table("wx_raw_messages")\
    .delete()\
    .gte("timestamp", "2025-01-15T00:00:00")\
    .lt("timestamp", "2025-01-16T00:00:00")\
    .execute()
```

---

## 📚 相关文档

- [系统概览](../README.md)
- [快速开始](./QUICKSTART.md)
- [Search API文档](./SEARCH_API.md)
- [配置指南](../CONFIGURATION.md)

---

## 🎯 下一步

1. ✅ **准备数据**: 导出微信群聊消息
2. ✅ **运行测试**: 用少量数据测试流程
3. ✅ **批量处理**: 处理历史数据
4. ✅ **日常使用**: 建立每日处理流程
5. ✅ **监控优化**: 跟踪推荐准确率

开始使用吧！🚀
