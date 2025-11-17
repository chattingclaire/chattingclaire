"""Context management for agents.

DEPRECATED: Use enhanced_context.EnhancedContextManager instead.
This file kept for backward compatibility.
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from database import get_db
from .embeddings import EmbeddingManager
from .enhanced_context import get_enhanced_context_manager


class ContextManager:
    """
    Manage context and memory for agents.

    NOTE: This is a wrapper around EnhancedContextManager for backward compatibility.
    Use EnhancedContextManager directly for full features.
    """

    def __init__(self):
        self.db = get_db()
        self.embedding_manager = EmbeddingManager()
        self.enhanced = get_enhanced_context_manager()  # Use enhanced version
        logger.info("Context manager initialized (using EnhancedContextManager)")

    def get_relevant_context(
        self,
        query: str,
        sources: List[str] = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Delegate to enhanced context manager"""
        return self.enhanced.search_similar_content(
            query=query,
            source_filter=sources[0] if sources else None,
            limit=limit,
            threshold=threshold
        )

    def get_ticker_context(self, ticker: str) -> Dict[str, Any]:
        """Delegate to enhanced context manager"""
        return self.enhanced.get_ticker_context(ticker)

    def rewrite_query(self, query: str, conversation_history: List[Dict] = None) -> str:
        """Delegate to enhanced context manager"""
        return self.enhanced.rewrite_query(query, conversation_history)
