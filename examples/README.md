# Usage Examples

This directory contains practical examples demonstrating how to use the Multi-Agent Trading System.

## 📁 Files

### `search_usage_example.py`
Comprehensive examples for the Memory & Context Engineering system.

**Examples included:**
1. **Basic Semantic Search** - Search WeChat messages and external data
2. **Query Rewriting** - LLM-powered query optimization with context
3. **Ticker Context** - Get comprehensive stock information
4. **Bulk Indexing** - Index WeChat messages in batches
5. **Conversational Memory** - Maintain conversation context
6. **Multi-Source Search** - Search across different data sources
7. **External Data Indexing** - Index news, tweets, Reddit posts

**Usage:**
```bash
python examples/search_usage_example.py
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Make sure `.env` file is properly configured with:
- `OPENAI_API_KEY` - For embeddings and query rewriting
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `ANTHROPIC_API_KEY` - For Claude agents
- `TUSHARE_TOKEN` - For Chinese stock data

### 3. Initialize Database
Run the schema in Supabase:
```sql
-- In Supabase SQL Editor
-- Copy contents from database/schema.sql
```

### 4. Run Examples
```bash
# Run all search examples
python examples/search_usage_example.py

# Or import specific examples
python -c "from examples.search_usage_example import example_1_basic_search; example_1_basic_search()"
```

## 📚 Example Breakdown

### Example 1: Basic Search
```python
from memory.enhanced_context import get_enhanced_context_manager

ctx = get_enhanced_context_manager()

results = ctx.search_similar_content(
    query="贵州茅台的业绩",
    source_filter="wx_raw_messages",
    limit=10,
    threshold=0.7
)

for result in results:
    print(f"Similarity: {result['similarity_score']:.2f}")
    print(f"Content: {result['content']}")
```

### Example 2: Query Rewriting
```python
# Vague query with pronoun
query = "它的业绩怎么样"

# Conversation history provides context
history = [
    {"role": "user", "content": "告诉我贵州茅台的情况"}
]

# LLM rewrites to clear query
rewritten = ctx.rewrite_query(query, history)
# Result: "贵州茅台的财务业绩表现如何"
```

### Example 3: Comprehensive Context
```python
# Get all available information for a ticker
context = ctx.get_ticker_context(
    ticker="600519",
    include_history=True,
    days_back=30
)

# Returns:
# - wx_signals: WeChat discussions
# - external_signals: News, Twitter, Reddit
# - picks: Stock selection results
# - fundamentals: Financial data
# - strategies: Strategy recommendations
# - trades: Execution history
```

### Example 4: Bulk Indexing
```python
messages = [
    {
        "message_id": "msg_001",
        "content": "贵州茅台今天涨停了",
        "sender": "张三",
        "timestamp": "2025-01-15T10:30:00",
        "chat_id": "group_123"
    },
    # ... more messages
]

# Index in batches of 100
indexed_count = ctx.index_wechat_messages(
    messages=messages,
    batch_size=100
)
```

### Example 5: Conversational Memory
```python
# Add conversation exchanges
ctx.add_to_conversation(
    user_message="贵州茅台的情况怎么样?",
    assistant_message="贵州茅台是中国最大的白酒企业..."
)

# Get full history
history = ctx.get_conversation_history()

# Use in query rewriting
rewritten = ctx.rewrite_query("它的PE高吗?", history)
```

## 🔧 Customization

### Adjusting Similarity Threshold
```python
# Strict matching (high precision)
results = ctx.search_similar_content(query="...", threshold=0.9)

# Balanced (recommended)
results = ctx.search_similar_content(query="...", threshold=0.7)

# Loose matching (high recall)
results = ctx.search_similar_content(query="...", threshold=0.5)
```

### Filtering by Source
```python
# WeChat only
ctx.search_similar_content(query="...", source_filter="wx_raw_messages")

# External only
ctx.search_similar_content(query="...", source_filter="external_raw_items")

# All sources
ctx.search_similar_content(query="...", source_filter=None)
```

### Batch Size Optimization
```python
# Small batches (safer, slower)
ctx.index_wechat_messages(messages, batch_size=50)

# Medium batches (balanced)
ctx.index_wechat_messages(messages, batch_size=100)

# Large batches (faster, more memory)
ctx.index_wechat_messages(messages, batch_size=500)
```

## 🧪 Testing

Before running examples, test system integrity:
```bash
python test_search_system.py
```

This checks:
- ✓ All dependencies installed
- ✓ Environment variables configured
- ✓ Database connectivity
- ✓ Vector store operational
- ✓ Embedding service working

## 📊 Performance Tips

1. **Index data in bulk** rather than one-by-one
2. **Cache frequently accessed contexts** using the ticker context feature
3. **Adjust thresholds** based on your use case
4. **Use source filters** to narrow search scope
5. **Monitor API rate limits** for OpenAI embeddings

## 🔗 Related Documentation

- [Search API Documentation](../docs/SEARCH_API.md)
- [Quick Start Guide](../docs/QUICKSTART.md)
- [System Architecture](../README.md)
- [Data Sources](../docs/DATA_SOURCES.md)

## 💡 Tips

- Start with Example 1 to understand basic search
- Use Example 4 to populate your database with test data
- Example 3 is most useful for agent decision-making
- Example 2 is crucial for chat interfaces
- Example 5 enables multi-turn conversations

## 🐛 Troubleshooting

### "No results found"
- Make sure data is indexed first (Example 4 or 7)
- Lower the similarity threshold
- Check if query matches indexed content language

### "Connection error"
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Ensure database schema is initialized
- Check network connectivity

### "OpenAI API error"
- Verify OPENAI_API_KEY is valid
- Check API rate limits
- Ensure sufficient API credits

## 📈 Next Steps

After trying these examples:
1. Index your own WeChat data
2. Integrate with the agent pipeline
3. Build custom search interfaces
4. Deploy the API server
5. Create your own examples!
