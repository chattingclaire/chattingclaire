"""
Search API Endpoints

Provides comprehensive search functionality across all data sources.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from memory.enhanced_context import get_enhanced_context_manager

# Create router
router = APIRouter(prefix="/api/search", tags=["Search"])

# Get context manager
context_manager = get_enhanced_context_manager()


# ========================================
# Request/Response Models
# ========================================

class SemanticSearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., description="Search query")
    source_filter: Optional[str] = Field(None, description="Filter by source table")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")


class SemanticSearchResponse(BaseModel):
    """Semantic search response"""
    query: str
    rewritten_query: Optional[str] = None
    results: List[Dict[str, Any]]
    total_found: int
    execution_time_ms: float


class TickerContextRequest(BaseModel):
    """Ticker context request"""
    ticker: str = Field(..., description="Stock ticker symbol")
    include_history: bool = Field(True, description="Include trade history")
    days_back: int = Field(30, ge=1, le=365, description="Days to look back")


class QueryRewriteRequest(BaseModel):
    """Query rewrite request"""
    query: str = Field(..., description="Original query")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, description="Conversation history for context"
    )


class IndexRequest(BaseModel):
    """Bulk indexing request"""
    items: List[Dict[str, Any]] = Field(..., description="Items to index")
    source_table: str = Field(..., description="Source table name")
    batch_size: int = Field(100, ge=1, le=1000, description="Batch size")


# ========================================
# Search Endpoints
# ========================================

@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    Semantic search across all data sources

    Uses OpenAI embeddings + Supabase pgvector for similarity search.

    Example:
    ```json
    {
      "query": "贵州茅台最近的消息",
      "source_filter": "wx_raw_messages",
      "limit": 10,
      "threshold": 0.7
    }
    ```
    """
    try:
        start_time = datetime.now()

        # Optional: Rewrite query for better retrieval
        rewritten_query = context_manager.rewrite_query(request.query)

        # Perform search
        results = context_manager.search_similar_content(
            query=rewritten_query,
            source_filter=request.source_filter,
            limit=request.limit,
            threshold=request.threshold
        )

        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        return SemanticSearchResponse(
            query=request.query,
            rewritten_query=rewritten_query if rewritten_query != request.query else None,
            results=results,
            total_found=len(results),
            execution_time_ms=execution_time
        )

    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{ticker}")
async def get_ticker_context(
    ticker: str,
    include_history: bool = Query(True),
    days_back: int = Query(30, ge=1, le=365)
):
    """
    Get comprehensive context for a ticker

    Returns:
    - WeChat signals
    - External signals
    - Stock picks
    - Fundamentals
    - Strategies
    - Trade history (optional)

    Example: `/api/search/ticker/600519?include_history=true&days_back=30`
    """
    try:
        context = context_manager.get_ticker_context(
            ticker=ticker,
            include_history=include_history,
            days_back=days_back
        )

        return {
            "success": True,
            "ticker": ticker,
            "context": context,
            "retrieved_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Get ticker context error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite-query")
async def rewrite_query(request: QueryRewriteRequest):
    """
    Rewrite user query for better retrieval

    Uses LLM to expand abbreviations, resolve references, and improve clarity.

    Example:
    ```json
    {
      "query": "它的业绩怎么样",
      "conversation_history": [
        {"role": "user", "content": "告诉我贵州茅台的情况"},
        {"role": "assistant", "content": "贵州茅台是..."}
      ]
    }
    ```

    Returns: "贵州茅台的财务业绩表现如何"
    """
    try:
        rewritten = context_manager.rewrite_query(
            query=request.query,
            conversation_history=request.conversation_history
        )

        return {
            "original_query": request.query,
            "rewritten_query": rewritten,
            "improved": rewritten != request.query
        }

    except Exception as e:
        logger.error(f"Query rewrite error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar-tickers/{ticker}")
async def find_similar_tickers(
    ticker: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Find similar stocks based on:
    - Similar WeChat discussion patterns
    - Similar fundamentals
    - Similar sentiment

    Example: `/api/search/similar-tickers/600519?limit=10`
    """
    try:
        # Get ticker context as query
        context = context_manager.get_ticker_context(ticker, include_history=False)

        # Build search query from context
        query_parts = []
        if context.get("fundamentals"):
            sector = context["fundamentals"].get("sector")
            if sector:
                query_parts.append(sector)

        # Search for similar content
        query = f"{ticker} " + " ".join(query_parts)
        results = context_manager.search_similar_content(
            query=query,
            limit=limit * 2,  # Get more, then filter
            threshold=0.6
        )

        # Extract unique tickers from results
        similar_tickers = set()
        for result in results:
            # Extract tickers from metadata or content
            metadata = result.get("metadata", {})
            # TODO: Better ticker extraction logic
            pass

        return {
            "ticker": ticker,
            "similar_tickers": list(similar_tickers)[:limit],
            "based_on": query_parts
        }

    except Exception as e:
        logger.error(f"Find similar tickers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Indexing Endpoints
# ========================================

@router.post("/index/wechat")
async def index_wechat_messages(request: IndexRequest):
    """
    Bulk index WeChat messages into vector store

    Example:
    ```json
    {
      "items": [
        {
          "message_id": "123",
          "content": "贵州茅台今天涨了",
          "sender": "张三",
          "timestamp": "2025-01-01T10:00:00"
        }
      ],
      "source_table": "wx_raw_messages",
      "batch_size": 100
    }
    ```
    """
    try:
        indexed_count = context_manager.index_wechat_messages(
            messages=request.items,
            batch_size=request.batch_size
        )

        return {
            "success": True,
            "indexed_count": indexed_count,
            "total_items": len(request.items)
        }

    except Exception as e:
        logger.error(f"Index WeChat messages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/external")
async def index_external_items(request: IndexRequest):
    """
    Bulk index external items into vector store

    Example:
    ```json
    {
      "items": [
        {
          "source_id": "123",
          "source": "twitter",
          "content": "AAPL earnings beat",
          "url": "https://..."
        }
      ],
      "source_table": "external_raw_items",
      "batch_size": 100
    }
    ```
    """
    try:
        indexed_count = context_manager.index_external_items(
            items=request.items,
            batch_size=request.batch_size
        )

        return {
            "success": True,
            "indexed_count": indexed_count,
            "total_items": len(request.items)
        }

    except Exception as e:
        logger.error(f"Index external items error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Analytics Endpoints
# ========================================

@router.get("/stats")
async def get_search_stats():
    """
    Get search system statistics

    Returns:
    - Total indexed documents
    - Documents by source
    - Recent searches
    """
    try:
        # TODO: Implement stats collection
        return {
            "total_documents": 0,
            "by_source": {},
            "recent_searches": []
        }

    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def search_health_check():
    """Check search system health"""
    try:
        # Test semantic search
        test_result = context_manager.search_similar_content(
            query="test",
            limit=1,
            threshold=0.0
        )

        return {
            "status": "healthy",
            "vector_store": "connected",
            "embedding_service": "connected",
            "test_search": "passed"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
