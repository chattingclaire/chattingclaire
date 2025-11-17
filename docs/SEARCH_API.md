# 搜索 API 完整文档

## 📚 概览

完整的**Memory & Context Engineering**实现，基于：
- **LangChain**: 对话记忆、文档处理
- **OpenAI Embeddings**: text-embedding-3-large
- **Supabase pgvector**: 向量存储和相似度搜索
- **FastAPI**: RESTful API接口

## 🏗️ 架构

```
┌─────────────────────────────────────────────┐
│        Search & Memory System                │
└─────────────────────────────────────────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
┌─────▼──────┐ ┌───▼────┐ ┌─────▼──────┐
│ LangChain  │ │ OpenAI │ │  Supabase  │
│   Memory   │ │Embedding│ │  pgvector  │
└────────────┘ └────────┘ └────────────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
         ┌──────────▼──────────┐
         │    Search API        │
         │  (8+ endpoints)      │
         └─────────────────────┘
```

## 🚀 核心功能

### 1. 语义搜索（Semantic Search）
- ✅ 基于向量相似度的智能搜索
- ✅ 支持跨表搜索（WeChat、External、所有数据源）
- ✅ 可配置相似度阈值
- ✅ 自动查询重写优化

### 2. 上下文检索（Context Retrieval）
- ✅ 股票全景上下文
- ✅ 多源数据聚合（WeChat + External + Fundamentals + Strategies + Trades）
- ✅ 时间范围过滤
- ✅ 智能去重和排序

### 3. 对话记忆（Conversational Memory）
- ✅ 基于 LangChain 的对话历史管理
- ✅ 自动上下文传递
- ✅ 对话总结（避免token超限）

### 4. 查询重写（Query Rewriting）
- ✅ LLM驱动的查询理解
- ✅ 代词解析（"它" → "贵州茅台"）
- ✅ 缩写展开
- ✅ 上下文补全

### 5. 批量索引（Bulk Indexing）
- ✅ WeChat消息批量入库
- ✅ 外部数据批量索引
- ✅ 自动向量化
- ✅ 增量更新

## 📡 API 接口

### Base URL
```
http://localhost:8000/api/search
```

---

### 1. 语义搜索

**POST** `/api/search/semantic`

使用OpenAI embeddings进行相似度搜索。

**Request Body:**
```json
{
  "query": "贵州茅台最近的消息",
  "source_filter": "wx_raw_messages",
  "limit": 10,
  "threshold": 0.7
}
```

**Parameters:**
- `query` (string, required): 搜索查询
- `source_filter` (string, optional): 过滤数据源
  - `"wx_raw_messages"` - 仅WeChat消息
  - `"external_raw_items"` - 仅外部信息
  - `null` - 搜索所有
- `limit` (int, optional): 最大结果数 (1-100, 默认10)
- `threshold` (float, optional): 相似度阈值 (0.0-1.0, 默认0.7)

**Response:**
```json
{
  "query": "贵州茅台最近的消息",
  "rewritten_query": "贵州茅台（股票代码600519）的最新新闻和公告",
  "results": [
    {
      "content": "茅台今天又创新高了...",
      "metadata": {
        "message_id": "123",
        "sender": "张三",
        "timestamp": "2025-01-01T10:00:00",
        "chat_id": "group_456"
      },
      "similarity_score": 0.89
    }
  ],
  "total_found": 5,
  "execution_time_ms": 45.2
}
```

**示例（curl）:**
```bash
curl -X POST "http://localhost:8000/api/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "贵州茅台",
    "limit": 5,
    "threshold": 0.7
  }'
```

---

### 2. 获取股票上下文

**GET** `/api/search/ticker/{ticker}`

获取股票的全景信息（WeChat信号、外部数据、基本面、策略等）。

**URL Parameters:**
- `ticker` (string, required): 股票代码（如 `600519`）

**Query Parameters:**
- `include_history` (bool, optional): 是否包含交易历史（默认true）
- `days_back` (int, optional): 回溯天数（1-365，默认30）

**Response:**
```json
{
  "success": true,
  "ticker": "600519",
  "context": {
    "ticker": "600519",
    "retrieved_at": "2025-01-17T10:00:00",
    "wx_signals": [
      {
        "content": "茅台Q4业绩超预期",
        "similarity_score": 0.92,
        "metadata": {...}
      }
    ],
    "external_signals": [...],
    "picks": [
      {
        "action": "BUY",
        "confidence_score": 0.88,
        "reasons": [...]
      }
    ],
    "fundamentals": {
      "pe_ratio": 35.5,
      "revenue": 120000000000,
      ...
    },
    "strategies": [...],
    "trades": [...]
  }
}
```

**示例（curl）:**
```bash
curl "http://localhost:8000/api/search/ticker/600519?include_history=true&days_back=30"
```

---

### 3. 查询重写

**POST** `/api/search/rewrite-query`

使用LLM重写模糊查询，使其更清晰、更适合检索。

**Request Body:**
```json
{
  "query": "它的业绩怎么样",
  "conversation_history": [
    {
      "role": "user",
      "content": "告诉我贵州茅台的情况"
    },
    {
      "role": "assistant",
      "content": "贵州茅台是中国最大的白酒企业..."
    }
  ]
}
```

**Response:**
```json
{
  "original_query": "它的业绩怎么样",
  "rewritten_query": "贵州茅台的财务业绩表现如何",
  "improved": true
}
```

**使用场景：**
- 用户输入模糊（"它"、"这家公司"）
- 缩写和简称（"茅台" → "贵州茅台"）
- 口语化查询转专业术语

---

### 4. 查找相似股票

**GET** `/api/search/similar-tickers/{ticker}`

基于多维度相似性（行业、讨论模式、基本面）查找相似股票。

**URL Parameters:**
- `ticker` (string, required): 参考股票代码

**Query Parameters:**
- `limit` (int, optional): 最大结果数（1-50，默认10）

**Response:**
```json
{
  "ticker": "600519",
  "similar_tickers": [
    "000858",  // 五粮液
    "000799",  // 酒鬼酒
    "600702"   // 舍得酒业
  ],
  "based_on": ["白酒行业", "高端消费"]
}
```

---

### 5. 索引WeChat消息

**POST** `/api/search/index/wechat`

批量索引WeChat消息到向量库。

**Request Body:**
```json
{
  "items": [
    {
      "message_id": "123",
      "content": "贵州茅台今天又创新高了，600519看到2800",
      "sender": "张三",
      "timestamp": "2025-01-01T10:00:00",
      "chat_id": "group_456"
    },
    {
      "message_id": "124",
      "content": "估值有点贵了",
      "sender": "李四",
      "timestamp": "2025-01-01T10:05:00",
      "chat_id": "group_456"
    }
  ],
  "source_table": "wx_raw_messages",
  "batch_size": 100
}
```

**Response:**
```json
{
  "success": true,
  "indexed_count": 2,
  "total_items": 2
}
```

---

### 6. 索引外部数据

**POST** `/api/search/index/external`

批量索引外部信息到向量库。

**Request Body:**
```json
{
  "items": [
    {
      "source_id": "tweet_123",
      "source": "twitter",
      "content": "AAPL beats earnings expectations",
      "url": "https://twitter.com/...",
      "published_at": "2025-01-01T14:00:00"
    }
  ],
  "source_table": "external_raw_items",
  "batch_size": 100
}
```

---

### 7. 系统统计

**GET** `/api/search/stats`

获取搜索系统统计信息。

**Response:**
```json
{
  "total_documents": 15230,
  "by_source": {
    "wx_raw_messages": 10500,
    "external_raw_items": 4730
  },
  "recent_searches": [
    {"query": "贵州茅台", "count": 45},
    {"query": "特斯拉", "count": 32}
  ]
}
```

---

### 8. 健康检查

**GET** `/api/search/health`

检查搜索系统健康状态。

**Response:**
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "embedding_service": "connected",
  "test_search": "passed"
}
```

---

## 💻 Python SDK 使用示例

### 基础搜索

```python
from memory.enhanced_context import get_enhanced_context_manager

# 获取context manager
ctx = get_enhanced_context_manager()

# 语义搜索
results = ctx.search_similar_content(
    query="贵州茅台的业绩",
    source_filter="wx_raw_messages",
    limit=10,
    threshold=0.7
)

for result in results:
    print(f"相似度: {result['similarity_score']:.2f}")
    print(f"内容: {result['content'][:100]}")
```

### 获取股票上下文

```python
# 获取600519的全景信息
context = ctx.get_ticker_context(
    ticker="600519",
    include_history=True,
    days_back=30
)

print(f"WeChat信号: {len(context['wx_signals'])}")
print(f"基本面数据: {context['fundamentals']}")
print(f"策略建议: {len(context['strategies'])}")
```

### 查询重写

```python
# 重写模糊查询
original = "它最近怎么样"
rewritten = ctx.rewrite_query(
    query=original,
    conversation_history=[
        {"role": "user", "content": "贵州茅台的情况"},
        {"role": "assistant", "content": "..."}
    ]
)

print(f"原查询: {original}")
print(f"重写后: {rewritten}")
```

### 批量索引

```python
# 索引WeChat消息
messages = [
    {
        "message_id": "123",
        "content": "茅台涨停了",
        "sender": "张三",
        "timestamp": "2025-01-01T10:00:00"
    },
    # ... more messages
]

indexed = ctx.index_wechat_messages(
    messages=messages,
    batch_size=100
)

print(f"已索引: {indexed} 条消息")
```

---

## 🔧 配置说明

### 环境变量（已配置）

```bash
# .env
OPENAI_API_KEY=sk-proj-0p7rJIOYOQ...  # ✅ 已配置
SUPABASE_URL=https://fftkazutsznpjvkqctvy.supabase.co  # ✅ 已配置
SUPABASE_KEY=eyJhbGci...  # ✅ 已配置
```

### 依赖安装

```bash
pip install -r requirements.txt

# 核心依赖：
# - langchain>=0.1.0
# - langchain-openai>=0.0.5
# - langchain-community>=0.0.20
# - faiss-cpu>=1.7.4
```

---

## 🚀 快速开始

### 1. 启动API服务器

```bash
cd dashboard/backend
uvicorn api:app --reload --port 8000
```

### 2. 访问API文档

```
http://localhost:8000/docs
```

交互式Swagger UI，可以直接测试所有接口。

### 3. 测试语义搜索

```bash
curl -X POST "http://localhost:8000/api/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "贵州茅台",
    "limit": 5
  }'
```

### 4. 索引数据

```python
from memory.enhanced_context import get_enhanced_context_manager

ctx = get_enhanced_context_manager()

# 索引WeChat消息
messages = [...]  # 你的消息列表
ctx.index_wechat_messages(messages)

# 现在可以搜索了
results = ctx.search_similar_content("茅台业绩")
```

---

## 📊 性能优化

### 1. 批量索引
```python
# 推荐batch_size
ctx.index_wechat_messages(messages, batch_size=100)
```

### 2. 缓存查询
```python
# LangChain自动缓存embedding
# 相同查询第二次会更快
```

### 3. 相似度阈值调优
```python
# 0.9 - 非常相似（精确匹配）
# 0.7 - 相似（推荐默认值）
# 0.5 - 相关
# 0.3 - 宽松
```

---

## 🐛 故障排查

### 问题 1：API返回500错误

**检查：**
```bash
# 确认OpenAI API Key有效
echo $OPENAI_API_KEY

# 测试连接
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### 问题 2：搜索结果为空

**原因：**
- 数据还未索引
- 相似度阈值过高

**解决：**
```python
# 降低阈值
results = ctx.search_similar_content(query="...", threshold=0.5)

# 检查索引状态
# 访问 /api/search/stats
```

### 问题 3：查询很慢

**优化：**
- 减少limit数量
- 使用source_filter过滤
- 升级到更快的embedding模型

---

## 📚 相关文档

- [LangChain文档](https://python.langchain.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Supabase pgvector](https://supabase.com/docs/guides/ai/vector-columns)

---

## ✅ 实现状态

| 功能 | 状态 | 说明 |
|------|------|------|
| 语义搜索 | ✅ 完成 | LangChain + pgvector |
| 上下文检索 | ✅ 完成 | 多源聚合 |
| 查询重写 | ✅ 完成 | LLM驱动 |
| 对话记忆 | ✅ 完成 | ConversationMemory |
| 批量索引 | ✅ 完成 | 批处理优化 |
| API接口 | ✅ 完成 | 8个endpoint |
| 文档 | ✅ 完成 | 完整API文档 |

**所有功能已完全实现并可用！** 🎉
