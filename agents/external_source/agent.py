"""External Source Agent - Aggregate non-WeChat information sources."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from agents.base_agent import BaseAgent


class ExternalSourceAgent(BaseAgent):
    """
    Agent 2: External Source Agent

    Aggregates information from Twitter, Reddit, GitHub, news, and regulatory filings.
    Weight: MAX 40% (WeChat is always >= 60%)
    """

    def __init__(self):
        super().__init__(
            agent_name="external_source_agent",
            prompt_file="external_source_agent.md",
        )

    def run(
        self,
        sources: List[str] = None,
        lookback_days: int = 7,
        tickers: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Collect external signals from configured sources.

        Args:
            sources: List of sources to query (if None, use all)
            lookback_days: How far back to collect data
            tickers: Specific tickers to track (if None, track all)

        Returns:
            Collection results with statistics
        """
        if sources is None:
            sources = ["twitter", "reddit", "news", "github", "edgar"]

        logger.info(f"Collecting from sources: {sources}")

        results = {
            "total_items": 0,
            "by_source": {},
            "errors": [],
        }

        # Collect from each source
        for source in sources:
            try:
                items = self._collect_from_source(source, lookback_days, tickers)
                results["by_source"][source] = len(items)
                results["total_items"] += len(items)

                # Insert into database
                if items:
                    self.db.insert_many("external_raw_items", items)
                    logger.info(f"Inserted {len(items)} items from {source}")

            except Exception as e:
                logger.error(f"Error collecting from {source}: {e}")
                results["errors"].append({"source": source, "error": str(e)})

        logger.info(f"External collection complete: {results}")
        return results

    def _collect_from_source(
        self, source: str, lookback_days: int, tickers: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect data from a specific source."""
        if source == "twitter":
            return self._collect_twitter(lookback_days, tickers)
        elif source == "reddit":
            return self._collect_reddit(lookback_days, tickers)
        elif source == "news":
            return self._collect_news(lookback_days, tickers)
        elif source == "github":
            return self._collect_github(lookback_days)
        elif source == "edgar":
            return self._collect_edgar(lookback_days, tickers)
        else:
            logger.warning(f"Unknown source: {source}")
            return []

    def _collect_twitter(
        self, lookback_days: int, tickers: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect tweets about stocks."""
        # TODO: Implement Twitter API integration
        logger.info(f"Collecting Twitter data (lookback: {lookback_days} days)")
        return []

    def _collect_reddit(
        self, lookback_days: int, tickers: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect Reddit posts from investing subreddits."""
        # TODO: Implement Reddit API integration (PRAW)
        logger.info(f"Collecting Reddit data (lookback: {lookback_days} days)")
        return []

    def _collect_news(
        self, lookback_days: int, tickers: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect news articles."""
        # TODO: Implement news aggregation
        logger.info(f"Collecting news (lookback: {lookback_days} days)")
        return []

    def _collect_github(self, lookback_days: int) -> List[Dict[str, Any]]:
        """Collect GitHub trending repositories."""
        # TODO: Implement GitHub trending
        logger.info(f"Collecting GitHub data (lookback: {lookback_days} days)")
        return []

    def _collect_edgar(
        self, lookback_days: int, tickers: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect SEC filings from EDGAR."""
        # TODO: Implement EDGAR filing collection
        logger.info(f"Collecting EDGAR filings (lookback: {lookback_days} days)")
        return []

    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text."""
        import re

        tickers = []

        # Cashtags: $AAPL
        cashtags = re.findall(r'\$([A-Z]{1,5})\b', text)
        tickers.extend(cashtags)

        # Explicit mentions: "Apple (AAPL)"
        explicit = re.findall(r'\(([A-Z]{1,5})\)', text)
        tickers.extend(explicit)

        return list(set(tickers))

    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment score (-1.0 to 1.0).

        TODO: Implement proper sentiment analysis (use LLM or sentiment model)
        """
        # Simple keyword-based for now
        bullish = ["bullish", "buy", "long", "moon", "rocket", "calls", "up", "gain"]
        bearish = ["bearish", "sell", "short", "crash", "puts", "down", "loss"]

        text_lower = text.lower()
        bull_count = sum(1 for word in bullish if word in text_lower)
        bear_count = sum(1 for word in bearish if word in text_lower)

        if bull_count + bear_count == 0:
            return 0.0

        return (bull_count - bear_count) / (bull_count + bear_count)
