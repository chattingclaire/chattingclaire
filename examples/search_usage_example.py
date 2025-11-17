#!/usr/bin/env python3
"""
Search System Usage Examples

Demonstrates how to use the Memory & Context Engineering system.

Prerequisites:
    - pip install -r requirements.txt
    - .env file configured
    - Supabase database initialized
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the enhanced context manager
from memory.enhanced_context import get_enhanced_context_manager


def example_1_basic_search():
    """Example 1: Basic semantic search"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Semantic Search")
    print("=" * 60)

    # Get context manager
    ctx = get_enhanced_context_manager()

    # Perform semantic search
    query = "贵州茅台的业绩"
    print(f"\nSearching for: {query}")

    results = ctx.search_similar_content(
        query=query,
        source_filter="wx_raw_messages",  # Only search WeChat messages
        limit=10,
        threshold=0.7  # 70% similarity threshold
    )

    print(f"\nFound {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. Similarity: {result['similarity_score']:.2f}")
        print(f"   Content: {result['content'][:100]}...")
        print(f"   Sender: {result['metadata'].get('sender', 'Unknown')}")
        print(f"   Time: {result['metadata'].get('timestamp', 'Unknown')}")
        print()


def example_2_query_rewriting():
    """Example 2: Query rewriting with conversation context"""
    print("\n" + "=" * 60)
    print("Example 2: Query Rewriting")
    print("=" * 60)

    ctx = get_enhanced_context_manager()

    # Conversation history
    history = [
        {"role": "user", "content": "告诉我贵州茅台的情况"},
        {"role": "assistant", "content": "贵州茅台是中国最大的白酒企业..."}
    ]

    # Vague query that references previous context
    vague_query = "它的业绩怎么样"

    print(f"\nOriginal query: {vague_query}")
    print(f"Conversation context: {len(history)} messages")

    # Rewrite query
    rewritten = ctx.rewrite_query(vague_query, history)

    print(f"Rewritten query: {rewritten}")

    # Now search with rewritten query
    results = ctx.search_similar_content(
        query=rewritten,
        limit=5,
        threshold=0.6
    )

    print(f"\nSearch results: {len(results)} found")


def example_3_ticker_context():
    """Example 3: Get comprehensive ticker context"""
    print("\n" + "=" * 60)
    print("Example 3: Comprehensive Ticker Context")
    print("=" * 60)

    ctx = get_enhanced_context_manager()

    ticker = "600519"  # 贵州茅台
    print(f"\nGetting context for: {ticker}")

    # Get all context
    context = ctx.get_ticker_context(
        ticker=ticker,
        include_history=True,
        days_back=30
    )

    print(f"\nContext retrieved:")
    print(f"  - WeChat signals: {len(context['wx_signals'])}")
    print(f"  - External signals: {len(context['external_signals'])}")
    print(f"  - Stock picks: {len(context['picks'])}")
    print(f"  - Strategies: {len(context['strategies'])}")

    if context.get('trades'):
        print(f"  - Trade history: {len(context['trades'])}")

    if context.get('fundamentals'):
        fund = context['fundamentals']
        print(f"\nFundamentals:")
        print(f"  - Company: {fund.get('company_name', 'N/A')}")
        print(f"  - Sector: {fund.get('sector', 'N/A')}")
        print(f"  - PE Ratio: {fund.get('pe_ratio', 'N/A')}")
        print(f"  - Market Cap: {fund.get('market_cap', 'N/A')}")


def example_4_bulk_indexing():
    """Example 4: Bulk index WeChat messages"""
    print("\n" + "=" * 60)
    print("Example 4: Bulk Indexing")
    print("=" * 60)

    ctx = get_enhanced_context_manager()

    # Sample messages to index
    messages = [
        {
            "message_id": "msg_001",
            "content": "贵州茅台今天涨停了，基本面持续向好",
            "sender": "张三",
            "timestamp": "2025-01-15T10:30:00",
            "chat_id": "group_123"
        },
        {
            "message_id": "msg_002",
            "content": "600519目标价2800，看好白酒板块",
            "sender": "李四",
            "timestamp": "2025-01-15T11:00:00",
            "chat_id": "group_123"
        },
        {
            "message_id": "msg_003",
            "content": "茅台Q4业绩超预期，建议关注",
            "sender": "王五",
            "timestamp": "2025-01-15T14:30:00",
            "chat_id": "group_456"
        },
        {
            "message_id": "msg_004",
            "content": "五粮液也不错，可以考虑配置",
            "sender": "赵六",
            "timestamp": "2025-01-15T15:00:00",
            "chat_id": "group_456"
        },
        {
            "message_id": "msg_005",
            "content": "白酒板块整体估值合理，长期看好",
            "sender": "孙七",
            "timestamp": "2025-01-15T16:00:00",
            "chat_id": "group_789"
        }
    ]

    print(f"\nIndexing {len(messages)} messages...")

    # Bulk index with batch size
    indexed_count = ctx.index_wechat_messages(
        messages=messages,
        batch_size=100
    )

    print(f"✓ Successfully indexed {indexed_count} messages")

    # Now search for them
    print("\nTesting search on newly indexed data...")
    results = ctx.search_similar_content(
        query="白酒板块",
        source_filter="wx_raw_messages",
        limit=5,
        threshold=0.5
    )

    print(f"Found {len(results)} results for '白酒板块'")


def example_5_conversational_memory():
    """Example 5: Using conversational memory"""
    print("\n" + "=" * 60)
    print("Example 5: Conversational Memory")
    print("=" * 60)

    ctx = get_enhanced_context_manager()

    # Simulate a conversation
    conversation = [
        ("用户", "贵州茅台的情况怎么样?"),
        ("助手", "贵州茅台是中国最大的白酒企业，股票代码600519..."),
        ("用户", "它的PE估值高吗?"),
        ("助手", "当前PE在35倍左右，相比历史水平处于中等位置..."),
        ("用户", "和五粮液比呢?"),
    ]

    print("\nSimulated conversation:")
    for role, message in conversation:
        print(f"{role}: {message}")

        if role == "用户":
            # Add to memory
            ctx.add_to_conversation(message, "")

    # Get conversation history
    history = ctx.get_conversation_history()
    print(f"\nConversation history: {len(history)} messages")

    # Use history for query rewriting
    last_query = conversation[-1][1]
    rewritten = ctx.rewrite_query(last_query, history)

    print(f"\nLast query: {last_query}")
    print(f"Rewritten with context: {rewritten}")

    # Clear conversation
    ctx.clear_conversation()
    print("\n✓ Conversation memory cleared")


def example_6_multi_source_search():
    """Example 6: Search across multiple sources"""
    print("\n" + "=" * 60)
    print("Example 6: Multi-Source Search")
    print("=" * 60)

    ctx = get_enhanced_context_manager()

    query = "贵州茅台业绩"

    # Search WeChat only
    print(f"\nSearching WeChat only for: {query}")
    wx_results = ctx.search_similar_content(
        query=query,
        source_filter="wx_raw_messages",
        limit=5,
        threshold=0.6
    )
    print(f"WeChat results: {len(wx_results)}")

    # Search external only
    print(f"\nSearching External only for: {query}")
    external_results = ctx.search_similar_content(
        query=query,
        source_filter="external_raw_items",
        limit=5,
        threshold=0.6
    )
    print(f"External results: {len(external_results)}")

    # Search all sources
    print(f"\nSearching ALL sources for: {query}")
    all_results = ctx.search_similar_content(
        query=query,
        source_filter=None,  # No filter = search all
        limit=10,
        threshold=0.6
    )
    print(f"Total results: {len(all_results)}")

    # Show source breakdown
    sources = {}
    for result in all_results:
        source = result['metadata'].get('source_table', 'unknown')
        sources[source] = sources.get(source, 0) + 1

    print("\nResults by source:")
    for source, count in sources.items():
        print(f"  - {source}: {count}")


def example_7_index_external_items():
    """Example 7: Index external data sources"""
    print("\n" + "=" * 60)
    print("Example 7: Index External Items")
    print("=" * 60)

    ctx = get_enhanced_context_manager()

    # Sample external items
    items = [
        {
            "source_id": "tweet_001",
            "source": "twitter",
            "content": "Moutai Q4 earnings beat expectations, revenue up 15% YoY",
            "url": "https://twitter.com/example/status/123",
            "published_at": "2025-01-15T08:00:00"
        },
        {
            "source_id": "news_001",
            "source": "news",
            "content": "贵州茅台发布年度报告，营收破千亿",
            "url": "https://news.example.com/moutai-annual-report",
            "published_at": "2025-01-15T09:30:00"
        },
        {
            "source_id": "reddit_001",
            "source": "reddit",
            "content": "Chinese liquor stocks looking strong, especially KWEICHOW MOUTAI",
            "url": "https://reddit.com/r/stocks/comments/abc123",
            "published_at": "2025-01-15T12:00:00"
        }
    ]

    print(f"\nIndexing {len(items)} external items...")

    indexed_count = ctx.index_external_items(
        items=items,
        batch_size=100
    )

    print(f"✓ Successfully indexed {indexed_count} items")

    # Search for them
    print("\nTesting search on newly indexed external data...")
    results = ctx.search_similar_content(
        query="Moutai earnings",
        source_filter="external_raw_items",
        limit=5,
        threshold=0.5
    )

    print(f"Found {len(results)} results for 'Moutai earnings'")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("MEMORY & CONTEXT ENGINEERING - USAGE EXAMPLES")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}")

    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ WARNING: OPENAI_API_KEY not set in environment")
        print("Make sure .env file is configured correctly")
        return

    if not os.getenv("SUPABASE_URL"):
        print("\n⚠ WARNING: SUPABASE_URL not set in environment")
        return

    try:
        # Run examples
        example_1_basic_search()
        example_2_query_rewriting()
        example_3_ticker_context()
        example_4_bulk_indexing()
        example_5_conversational_memory()
        example_6_multi_source_search()
        example_7_index_external_items()

        print("\n" + "=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
