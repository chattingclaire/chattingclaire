# 快速开始指南

完整的启动流程和测试指南。

## 📋 前置要求

- Python 3.8+
- pip
- Supabase账号（已配置）
- 所有API密钥（已在.env中）

## 🚀 第一步：安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 核心依赖包括：
# - langchain, langchain-openai, langchain-community
# - faiss-cpu (向量搜索)
# - supabase (数据库)
# - fastapi, uvicorn (API服务器)
# - anthropic (Claude API)
# - tushare, akshare, yfinance (数据源)
```

## 🧪 第二步：运行测试

```bash
# 测试系统完整性
python test_search_system.py
```

这个脚本会测试：
- ✓ 所有依赖是否正确安装
- ✓ 环境变量是否配置
- ✓ 数据源API是否可用
- ✓ Memory & Context系统是否工作
- ✓ FastAPI路由是否注册

## 📊 第三步：初始化数据库

在Supabase控制台运行：

```sql
-- 1. 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 运行schema文件
-- 复制 database/schema.sql 的内容到 SQL Editor 执行
```

或使用psql：

```bash
# 需要DATABASE_URL（从Supabase获取）
psql $DATABASE_URL < database/schema.sql
```

## 🎯 第四步：启动API服务器

```bash
# 开发模式（支持热重载）
cd dashboard/backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# 或者生产模式
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

启动后访问：
- **API文档**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/search/health

## 📝 第五步：测试Search API

### 1. Health Check

```bash
curl http://localhost:8000/api/search/health
```

期望返回：
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "embedding_service": "connected",
  "test_search": "passed"
}
```

### 2. 语义搜索

```bash
curl -X POST "http://localhost:8000/api/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "贵州茅台",
    "limit": 5,
    "threshold": 0.7
  }'
```

### 3. 查询重写

```bash
curl -X POST "http://localhost:8000/api/search/rewrite-query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "它的业绩怎么样",
    "conversation_history": [
      {"role": "user", "content": "贵州茅台的情况"}
    ]
  }'
```

### 4. 获取股票上下文

```bash
curl "http://localhost:8000/api/search/ticker/600519?include_history=true&days_back=30"
```

## 🔄 第六步：索引数据

### Python SDK

```python
from memory.enhanced_context import get_enhanced_context_manager

# 获取context manager
ctx = get_enhanced_context_manager()

# 索引WeChat消息
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
        "content": "600519目标价2800",
        "sender": "李四",
        "timestamp": "2025-01-15T11:00:00",
        "chat_id": "group_123"
    }
]

# 批量索引
indexed = ctx.index_wechat_messages(messages, batch_size=100)
print(f"已索引 {indexed} 条消息")

# 现在可以搜索了
results = ctx.search_similar_content(
    query="贵州茅台",
    source_filter="wx_raw_messages",
    limit=10,
    threshold=0.7
)

for result in results:
    print(f"相似度: {result['similarity_score']:.2f}")
    print(f"内容: {result['content']}")
    print(f"发送者: {result['metadata'].get('sender')}")
    print("---")
```

### REST API

```bash
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
      }
    ],
    "source_table": "wx_raw_messages",
    "batch_size": 100
  }'
```

## 🤖 第七步：运行完整Pipeline

```python
from orchestrator import TradingOrchestrator

# 创建orchestrator
orchestrator = TradingOrchestrator()

# 执行完整6-agent流程
results = orchestrator.run_pipeline(
    wechat_path="data/wechat/exports/group_chat_2025-01-15.json"
)

# 查看结果
print(f"WeChat信号: {len(results['wx_signals'])}")
print(f"股票选择: {len(results['stock_picks'])}")
print(f"策略建议: {len(results['strategies'])}")
print(f"执行交易: {len(results['trades'])}")
```

## 📚 常见问题

### Q1: ModuleNotFoundError

**问题**: `ModuleNotFoundError: No module named 'langchain'`

**解决**:
```bash
pip install -r requirements.txt
```

### Q2: OpenAI API错误

**问题**: `openai.AuthenticationError`

**解决**:
```bash
# 检查.env文件
cat .env | grep OPENAI_API_KEY

# 确保API key有效
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### Q3: Supabase连接错误

**问题**: `supabase.errors.APIError`

**解决**:
1. 确认SUPABASE_URL和SUPABASE_KEY正确
2. 检查pgvector扩展已启用
3. 确认embeddings表已创建

### Q4: 搜索返回空结果

**原因**: 数据还未索引

**解决**:
```python
# 先索引数据
ctx.index_wechat_messages(messages)

# 或降低相似度阈值
results = ctx.search_similar_content(query="...", threshold=0.5)
```

## 🔧 开发工作流

### 1. 修改代码后

```bash
# API会自动重载（如果使用--reload）
# 或手动重启：
pkill -f "uvicorn api:app"
uvicorn dashboard.backend.api:app --reload
```

### 2. 添加新数据源

1. 在`tools/datasources/`创建新工具
2. 在`agents/`中使用新工具
3. 更新文档

### 3. 修改Agent提示词

编辑 `prompts/agents/{agent_name}.md`

### 4. 调整策略配置

编辑 `config/strategies.yaml`

## 🎯 下一步

1. ✅ **完成**: Memory & Context Engineering
2. ✅ **完成**: Search API (8个endpoint)
3. ✅ **完成**: 数据源集成 (Tushare + AKShare + Yahoo)
4. 🚧 **待做**: WeChat消息解析器
5. 🚧 **待做**: Agent TODO方法实现
6. 🚧 **待做**: 完整端到端测试
7. 🚧 **待做**: Dashboard前端

## 📖 相关文档

- [完整系统文档](../README.md)
- [Search API文档](./SEARCH_API.md)
- [数据源文档](./DATA_SOURCES.md)
- [配置指南](../CONFIGURATION.md)
- [数据库Schema](../database/schema.sql)

## 🆘 获取帮助

如果遇到问题：

1. 查看日志：`logs/`目录
2. 运行测试：`python test_search_system.py`
3. 检查配置：`.env`文件
4. 阅读文档：`docs/`目录
