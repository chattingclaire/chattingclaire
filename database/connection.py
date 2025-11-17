"""Database connection management using Supabase and SQLAlchemy."""

import os
from typing import Optional, Any, Dict, List
from supabase import create_client, Client
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class Database:
    """Database connection manager for Supabase and PostgreSQL."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.database_url = os.getenv("DATABASE_URL")

        if not all([self.supabase_url, self.supabase_key, self.database_url]):
            raise ValueError("Missing required database configuration in environment")

        # Initialize Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Initialize SQLAlchemy engine
        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False,
        )

        # Create session maker
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        logger.info("Database connection initialized")

    def get_session(self) -> Session:
        """Get a new SQLAlchemy session."""
        return self.SessionLocal()

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a raw SQL query and return results."""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into a table using Supabase client."""
        try:
            result = self.supabase.table(table).insert(data).execute()
            logger.debug(f"Inserted into {table}: {result.data}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error inserting into {table}: {e}")
            raise

    def insert_many(self, table: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Insert multiple rows into a table."""
        try:
            result = self.supabase.table(table).insert(data).execute()
            logger.debug(f"Inserted {len(data)} rows into {table}")
            return result.data
        except Exception as e:
            logger.error(f"Error inserting multiple rows into {table}: {e}")
            raise

    def update(
        self, table: str, data: Dict[str, Any], match: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update data in a table."""
        try:
            query = self.supabase.table(table).update(data)
            for key, value in match.items():
                query = query.eq(key, value)
            result = query.execute()
            logger.debug(f"Updated {table}: {result.data}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error updating {table}: {e}")
            raise

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Select data from a table."""
        try:
            query = self.supabase.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            if order:
                query = query.order(order)

            if limit:
                query = query.limit(limit)

            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}")
            raise

    def semantic_search(
        self,
        query_embedding: List[float],
        match_threshold: float = 0.7,
        match_count: int = 10,
        filter_table: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using vector embeddings."""
        try:
            result = self.supabase.rpc(
                "semantic_search",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": match_count,
                    "filter_table": filter_table,
                },
            ).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            raise

    def update_agent_status(
        self,
        agent_name: str,
        status: str,
        error_message: Optional[str] = None,
        metrics: Optional[Dict] = None,
    ):
        """Update agent status in the database."""
        try:
            data = {"status": status, "last_run_at": "NOW()"}

            if status == "error":
                data["last_error_at"] = "NOW()"
                data["error_message"] = error_message
                data["error_count"] = "error_count + 1"
            elif status == "idle":
                data["last_success_at"] = "NOW()"
                data["success_count"] = "success_count + 1"

            if metrics:
                data["metrics"] = metrics

            # Upsert agent status
            result = (
                self.supabase.table("agent_status")
                .upsert({"agent_name": agent_name, **data}, on_conflict="agent_name")
                .execute()
            )

            logger.debug(f"Updated status for {agent_name}: {status}")
            return result.data
        except Exception as e:
            logger.error(f"Error updating agent status: {e}")
            raise

    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get or create global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db
