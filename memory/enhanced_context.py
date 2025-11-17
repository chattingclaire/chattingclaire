"""
Complete Memory & Context Engineering Implementation

Using LangChain + Supabase pgvector for production-grade memory management.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import SupabaseVectorStore

from database import get_db
from supabase import create_client


class EnhancedContextManager:
    """
    Production-grade Context & Memory Manager

    Features:
    1. Semantic Search (pgvector + OpenAI embeddings)
    2. Conversational Memory (LangChain)
    3. Context Retrieval (multi-source)
    4. Query Rewriting (LLM-powered)
    5. Caching & Performance optimization
    """

    def __init__(self):
        self.db = get_db()

        # Initialize OpenAI Embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-large"
        )

        # Initialize LLM for query rewriting
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo",
            temperature=0.3
        )

        # Conversation memory
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        # Initialize Supabase Vector Store
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase_client = create_client(supabase_url, supabase_key)

        self.vector_store = SupabaseVectorStore(
            client=self.supabase_client,
            embedding=self.embeddings,
            table_name="embeddings",
            query_name="semantic_search"
        )

        logger.info("Enhanced Context Manager initialized with LangChain + Supabase")

    # ========================================
    # 1. Semantic Search
    # ========================================

    def search_similar_content(
        self,
        query: str,
        source_filter: Optional[str] = None,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using pgvector

        Args:
            query: Search query
            source_filter: Filter by source table
            limit: Max results
            threshold: Similarity threshold

        Returns:
            List of similar documents with scores
        """
        try:
            # Search using LangChain + Supabase
            docs = self.vector_store.similarity_search_with_relevance_scores(
                query=query,
                k=limit,
                filter={"source_table": source_filter} if source_filter else None
            )

            # Filter by threshold and format
            results = []
            for doc, score in docs:
                if score >= threshold:
                    results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": score
                    })

            logger.info(f"Semantic search found {len(results)} results for: {query[:50]}")
            return results

        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        source_table: str
    ) -> List[str]:
        """
        Add documents to vector store

        Args:
            texts: List of text content
            metadatas: List of metadata dicts
            source_table: Source table name

        Returns:
            List of document IDs
        """
        try:
            # Add source_table to metadata
            for meta in metadatas:
                meta["source_table"] = source_table
                meta["indexed_at"] = datetime.now().isoformat()

            # Create Document objects
            documents = [
                Document(page_content=text, metadata=meta)
                for text, meta in zip(texts, metadatas)
            ]

            # Add to vector store
            ids = self.vector_store.add_documents(documents)

            logger.info(f"Added {len(ids)} documents to vector store")
            return ids

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return []

    # ========================================
    # 2. Context Retrieval
    # ========================================

    def get_ticker_context(
        self,
        ticker: str,
        include_history: bool = True,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for a ticker

        Retrieves:
        - WeChat signals
        - External signals
        - Stock picks
        - Fundamentals
        - Strategies
        - Trade history
        """
        logger.info(f"Retrieving context for ticker: {ticker}")

        context = {
            "ticker": ticker,
            "retrieved_at": datetime.now().isoformat(),
            "wx_signals": self._get_wx_context(ticker, days_back),
            "external_signals": self._get_external_context(ticker, days_back),
            "picks": self._get_pick_context(ticker),
            "fundamentals": self._get_fundamental_context(ticker),
            "strategies": self._get_strategy_context(ticker),
        }

        if include_history:
            context["trades"] = self._get_trade_context(ticker, days_back)

        return context

    def _get_wx_context(self, ticker: str, days_back: int) -> List[Dict[str, Any]]:
        """Get WeChat signals for ticker"""
        try:
            cutoff = datetime.now() - timedelta(days=days_back)

            # Query using semantic search
            query = f"股票 {ticker} 消息 讨论"
            results = self.search_similar_content(
                query=query,
                source_filter="wx_raw_messages",
                limit=20,
                threshold=0.6
            )

            return results

        except Exception as e:
            logger.error(f"Error getting WX context: {e}")
            return []

    def _get_external_context(self, ticker: str, days_back: int) -> List[Dict[str, Any]]:
        """Get external signals for ticker"""
        try:
            cutoff = datetime.now() - timedelta(days=days_back)

            results = self.db.select(
                table="external_raw_items",
                filters={"extracted_tickers": f"%{ticker}%"},  # Contains
                limit=20
            )

            return results

        except Exception as e:
            logger.error(f"Error getting external context: {e}")
            return []

    def _get_pick_context(self, ticker: str) -> List[Dict[str, Any]]:
        """Get stock picks for ticker"""
        try:
            # Get from both pick tables
            wx_only = self.db.select(
                table="stock_picks_wx_only",
                filters={"ticker": ticker, "status": "active"},
                limit=10
            )

            wx_plus = self.db.select(
                table="stock_picks_wx_plus_external",
                filters={"ticker": ticker, "status": "active"},
                limit=10
            )

            return wx_only + wx_plus

        except Exception as e:
            logger.error(f"Error getting pick context: {e}")
            return []

    def _get_fundamental_context(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get fundamental data for ticker"""
        try:
            results = self.db.select(
                table="stock_fundamentals",
                filters={"ticker": ticker},
                limit=1,
                order="data_date.desc"
            )

            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error getting fundamental context: {e}")
            return None

    def _get_strategy_context(self, ticker: str) -> List[Dict[str, Any]]:
        """Get strategies for ticker"""
        try:
            return self.db.select(
                table="strategy_outputs",
                filters={"ticker": ticker},
                limit=10,
                order="created_at.desc"
            )
        except Exception as e:
            logger.error(f"Error getting strategy context: {e}")
            return []

    def _get_trade_context(self, ticker: str, days_back: int) -> List[Dict[str, Any]]:
        """Get trade history for ticker"""
        try:
            return self.db.select(
                table="executed_trades",
                filters={"ticker": ticker},
                limit=50,
                order="executed_at.desc"
            )
        except Exception as e:
            logger.error(f"Error getting trade context: {e}")
            return []

    # ========================================
    # 3. Query Rewriting (LLM-powered)
    # ========================================

    def rewrite_query(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Rewrite user query for better retrieval using LLM

        Examples:
        - "它的业绩怎么样" -> "贵州茅台的财务业绩表现如何"
        - "最近有什么消息" -> "贵州茅台最近的新闻和公告"
        """
        try:
            # Build prompt with history
            history_context = ""
            if conversation_history:
                recent = conversation_history[-3:]  # Last 3 messages
                history_context = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in recent
                ])

            prompt = f"""你是一个金融信息检索助手。请将用户的问题重写为更清晰、更适合检索的查询。

对话历史：
{history_context}

用户问题：{query}

请重写为完整、明确的查询语句（保持简洁）："""

            # Use LLM to rewrite
            response = self.llm.predict(prompt)
            rewritten = response.strip()

            logger.info(f"Query rewritten: '{query}' -> '{rewritten}'")
            return rewritten

        except Exception as e:
            logger.error(f"Query rewriting error: {e}")
            return query  # Fallback to original

    # ========================================
    # 4. Conversational Memory
    # ========================================

    def add_to_conversation(
        self,
        user_message: str,
        assistant_message: str
    ):
        """Add exchange to conversation memory"""
        self.conversation_memory.save_context(
            {"input": user_message},
            {"output": assistant_message}
        )

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        history = self.conversation_memory.load_memory_variables({})
        messages = history.get("chat_history", [])

        return [
            {"role": msg.type, "content": msg.content}
            for msg in messages
        ]

    def clear_conversation(self):
        """Clear conversation memory"""
        self.conversation_memory.clear()
        logger.info("Conversation memory cleared")

    # ========================================
    # 5. Bulk Indexing
    # ========================================

    def index_wechat_messages(
        self,
        messages: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Bulk index WeChat messages into vector store

        Args:
            messages: List of WeChat messages
            batch_size: Batch size for indexing

        Returns:
            Number of messages indexed
        """
        total_indexed = 0

        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]

            texts = [msg.get("content", "") for msg in batch]
            metadatas = [
                {
                    "message_id": msg.get("message_id"),
                    "sender": msg.get("sender"),
                    "timestamp": msg.get("timestamp"),
                    "chat_id": msg.get("chat_id"),
                }
                for msg in batch
            ]

            ids = self.add_documents(texts, metadatas, "wx_raw_messages")
            total_indexed += len(ids)

            logger.info(f"Indexed batch {i//batch_size + 1}: {len(ids)} messages")

        return total_indexed

    def index_external_items(
        self,
        items: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """Bulk index external items"""
        total_indexed = 0

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            texts = [item.get("content", "") for item in batch]
            metadatas = [
                {
                    "source": item.get("source"),
                    "source_id": item.get("source_id"),
                    "url": item.get("url"),
                    "published_at": item.get("published_at"),
                }
                for item in batch
            ]

            ids = self.add_documents(texts, metadatas, "external_raw_items")
            total_indexed += len(ids)

        return total_indexed


# Global instance
_enhanced_context_manager: Optional[EnhancedContextManager] = None


def get_enhanced_context_manager() -> EnhancedContextManager:
    """Get or create global enhanced context manager"""
    global _enhanced_context_manager
    if _enhanced_context_manager is None:
        _enhanced_context_manager = EnhancedContextManager()
    return _enhanced_context_manager
