# 微信消息导入 - 快速参考

## 🚀 最快上手方式

### 1️⃣ 准备数据（3种格式任选）

**方式A：创建JSON文件** `my_wechat.json`
```json
[
  {
    "sender": "张三",
    "content": "贵州茅台今天涨停了",
    "timestamp": "2025-01-15T10:30:00"
  },
  {
    "sender": "李四",
    "content": "600519目标价2800",
    "timestamp": "2025-01-15T10:35:00"
  }
]
```

**方式B：创建TXT文件** `my_wechat.txt`
```
[2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了
[2025-01-15 10:35:00] 李四: 600519目标价2800
```

**方式C：创建CSV文件** `my_wechat.csv`
```csv
sender,content,timestamp
张三,贵州茅台今天涨停了,2025-01-15T10:30:00
李四,600519目标价2800,2025-01-15T10:35:00
```

### 2️⃣ 运行示例脚本

```bash
# 运行完整示例（自动创建测试数据并处理）
python examples/wechat_input_example.py
```

### 3️⃣ 处理你自己的数据

```python
from orchestrator import TradingOrchestrator
import asyncio

async def main():
    orchestrator = TradingOrchestrator()

    # 处理你的微信数据
    results = await orchestrator.run_pipeline(
        wechat_export_path="my_wechat.json",
        mode="signals_only"  # 只生成信号，不执行交易
    )

    # 查看推荐
    for pick in results['stock_picks']:
        print(f"{pick['ticker']}: {pick['action']} - 置信度 {pick['confidence']:.1%}")

asyncio.run(main())
```

---

## 🎯 三种使用方式

### 方式1：完整Pipeline（推荐）
**适用场景**：完整的交易流程
```python
from orchestrator import TradingOrchestrator
import asyncio

orchestrator = TradingOrchestrator()
results = await orchestrator.run_pipeline(
    wechat_export_path="data/wechat/messages.json",
    mode="full"  # full=完整流程, signals_only=只分析
)
```

### 方式2：只处理微信（快速）
**适用场景**：只想解析微信数据
```python
from agents.wx_source.agent import WxSourceAgent

wx_agent = WxSourceAgent()
results = wx_agent.run(
    wechat_export_path="messages.json",
    export_type="auto"  # 自动检测格式
)
print(f"处理了 {results['processed_messages']} 条消息")
```

### 方式3：直接索引到搜索系统
**适用场景**：只想做语义搜索
```python
from memory.enhanced_context import get_enhanced_context_manager

ctx = get_enhanced_context_manager()

messages = [
    {"content": "贵州茅台涨停", "sender": "张三",
     "timestamp": "2025-01-15T10:30:00", "chat_id": "group_1"}
]

indexed = ctx.index_wechat_messages(messages)
print(f"已索引 {indexed} 条")

# 搜索
results = ctx.search_similar_content("茅台", limit=10)
```

---

## 📋 数据格式要求

### 最简格式（只需2个字段）
```json
[
  {"content": "贵州茅台涨停", "sender": "张三"}
]
```

### 完整格式（推荐）
```json
[
  {
    "sender": "张三",
    "content": "贵州茅台今天涨停了",
    "timestamp": "2025-01-15T10:30:00",
    "chat_name": "股票群",
    "message_type": "text"
  }
]
```

### 字段说明
| 字段 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `content` | ✅ | 消息内容 | "贵州茅台涨停" |
| `sender` | 推荐 | 发送者 | "张三" |
| `timestamp` | 推荐 | 时间戳 | "2025-01-15T10:30:00" |
| `chat_name` | 可选 | 群名称 | "股票交流群" |
| `message_type` | 可选 | 消息类型 | "text" / "image" / "link" |

---

## 💡 实用技巧

### 技巧1：批量处理多个文件
```python
from pathlib import Path

for file in Path("data/wechat").glob("*.json"):
    results = wx_agent.run(wechat_export_path=str(file))
    print(f"{file.name}: {results['processed_messages']} 条")
```

### 技巧2：提取股票代码
系统自动识别：
- **A股代码**：6位数字 (600519, 000858, 300750)
- **美股代码**：大写字母 (AAPL, TSLA, NVDA)
- **港股代码**：4位数字 (0700, 9988)

### 技巧3：提高识别准确率
✅ **好的消息**：
```
"贵州茅台600519今天涨停，Q4业绩超预期，目标价2800，看好后续"
```
- 包含股票代码
- 有明确观点（看好/看空）
- 有理由说明

❌ **不好的消息**：
```
"哈哈"
"好的"
"收到"
```
- 太短
- 没有实质内容

---

## 🔍 验证数据是否导入成功

### 方法1：查询数据库
```python
from database.supabase_client import get_supabase_client

db = get_supabase_client()
messages = db.table("wx_raw_messages").select("*").limit(10).execute()

print(f"数据库中有 {len(messages.data)} 条消息")
```

### 方法2：搜索测试
```python
from memory.enhanced_context import get_enhanced_context_manager

ctx = get_enhanced_context_manager()
results = ctx.search_similar_content("贵州茅台", limit=5)

print(f"搜索到 {len(results)} 条相关消息")
for r in results:
    print(f"- {r['content'][:50]}...")
```

---

## 📚 相关文档

- **完整教程**：`docs/WECHAT_USAGE.md` - 详细使用指南
- **示例代码**：`examples/wechat_input_example.py` - 可运行的例子
- **Parser源码**：`tools/datasources/wechat_parser.py` - 解析器实现
- **Agent源码**：`agents/wx_source/agent.py` - 处理逻辑

---

## ❓ 常见问题

**Q: 支持什么格式？**
A: JSON, CSV, TXT, 或包含多个文件的目录

**Q: 必需哪些字段？**
A: 只需要 `content` 字段，其他都是可选的

**Q: 时间格式有要求吗？**
A: 支持多种格式：`2025-01-15T10:30:00`, `2025-01-15 10:30:00`, `2025/01/15 10:30:00`

**Q: 如何删除已导入的数据？**
A:
```python
db.table("wx_raw_messages").delete().eq("chat_id", "group_123").execute()
```

**Q: 可以导入历史数据吗？**
A: 可以！时间戳可以是任意日期

---

## 🎯 快速测试流程

```bash
# 1. 运行测试脚本
python examples/wechat_input_example.py

# 2. 查看生成的示例文件
ls data/wechat/examples/

# 3. 修改为你自己的数据
cp data/wechat/examples/sample_messages.json my_messages.json
# 编辑 my_messages.json

# 4. 处理你的数据
python -c "
from agents.wx_source.agent import WxSourceAgent
wx = WxSourceAgent()
results = wx.run('my_messages.json')
print(f'处理了 {results[\"processed_messages\"]} 条消息')
"
```

---

## ✨ 就这么简单！

1. 准备数据文件（JSON/CSV/TXT）
2. 运行 `python examples/wechat_input_example.py`
3. 开始使用！

需要更多帮助？查看 `docs/WECHAT_USAGE.md` 📖
