"""Selection Agent - Generate stock picks from signals."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from agents.base_agent import BaseAgent


class SelectionAgent(BaseAgent):
    """
    Agent 3: Selection Agent

    Generates concrete stock picks with buy/sell recommendations.
    CRITICAL: WeChat signals MUST have >= 60% weight.
    """

    def __init__(self):
        super().__init__(
            agent_name="selection_agent",
            prompt_file="selection_agent.md",
        )

    def run(
        self,
        mode: str = "both",  # "wx_only", "wx_plus_external", or "both"
        lookback_days: int = 7,
        min_confidence: float = 0.6,
    ) -> Dict[str, Any]:
        """
        Generate stock picks based on signals.

        Args:
            mode: Selection mode
            lookback_days: How far back to look for signals
            min_confidence: Minimum confidence threshold

        Returns:
            Selection results with generated picks
        """
        logger.info(f"Running selection in mode: {mode}")

        results = {
            "wx_only_picks": [],
            "wx_plus_external_picks": [],
            "total_picks": 0,
        }

        try:
            # Get signals from both agents
            wx_signals = self._get_wx_signals(lookback_days)
            external_signals = self._get_external_signals(lookback_days)

            logger.info(
                f"Found {len(wx_signals)} WeChat signals, "
                f"{len(external_signals)} external signals"
            )

            # Group signals by ticker
            wx_by_ticker = self._group_by_ticker(wx_signals)
            external_by_ticker = self._group_by_ticker(external_signals)

            # Get all tickers
            all_tickers = set(wx_by_ticker.keys()) | set(external_by_ticker.keys())

            for ticker in all_tickers:
                wx_sigs = wx_by_ticker.get(ticker, [])
                ext_sigs = external_by_ticker.get(ticker, [])

                # Generate WeChat-only pick if strong WX signal
                if mode in ["wx_only", "both"] and len(wx_sigs) >= 3:
                    pick = self._generate_wx_only_pick(ticker, wx_sigs, min_confidence)
                    if pick:
                        results["wx_only_picks"].append(pick)
                        self.db.insert("stock_picks_wx_only", pick)

                # Generate WeChat+External pick if both signals present
                if mode in ["wx_plus_external", "both"] and wx_sigs and ext_sigs:
                    pick = self._generate_wx_plus_external_pick(
                        ticker, wx_sigs, ext_sigs, min_confidence
                    )
                    if pick:
                        results["wx_plus_external_picks"].append(pick)
                        self.db.insert("stock_picks_wx_plus_external", pick)

            results["total_picks"] = (
                len(results["wx_only_picks"]) + len(results["wx_plus_external_picks"])
            )

            logger.info(f"Selection complete: {results['total_picks']} picks generated")
            return results

        except Exception as e:
            logger.error(f"Error in SelectionAgent.run: {e}")
            raise

    def _get_wx_signals(self, lookback_days: int) -> List[Dict[str, Any]]:
        """Get WeChat signals from database."""
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        query = """
            SELECT * FROM wx_raw_messages
            WHERE timestamp >= %s
            AND metadata->>'extracted_tickers' != '[]'
            ORDER BY timestamp DESC
        """
        # Simplified: return empty for now (TODO: implement proper query)
        return []

    def _get_external_signals(self, lookback_days: int) -> List[Dict[str, Any]]:
        """Get external signals from database."""
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        # Simplified: return empty for now (TODO: implement proper query)
        return []

    def _group_by_ticker(
        self, signals: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group signals by ticker."""
        grouped = {}
        for signal in signals:
            tickers = signal.get("extracted_tickers", [])
            for ticker in tickers:
                if ticker not in grouped:
                    grouped[ticker] = []
                grouped[ticker].append(signal)
        return grouped

    def _generate_wx_only_pick(
        self, ticker: str, wx_signals: List[Dict[str, Any]], min_confidence: float
    ) -> Optional[Dict[str, Any]]:
        """Generate a WeChat-only stock pick."""
        # Calculate aggregated metrics
        mention_count = len(wx_signals)
        sentiments = [s.get("metadata", {}).get("sentiment") for s in wx_signals]

        bullish_count = sum(1 for s in sentiments if s == "bullish")
        bearish_count = sum(1 for s in sentiments if s == "bearish")

        # Determine action
        if bullish_count > bearish_count:
            action = "BUY"
            sentiment_score = bullish_count / len(sentiments)
        elif bearish_count > bullish_count:
            action = "SELL"
            sentiment_score = -(bearish_count / len(sentiments))
        else:
            return None  # No clear signal

        # Calculate confidence
        confidence = self._calculate_wx_confidence(wx_signals, sentiment_score)

        if confidence < min_confidence:
            return None

        # Build pick
        pick = {
            "ticker": ticker,
            "company_name": self._get_company_name(ticker),
            "action": action,
            "confidence_score": confidence,
            "reasons": self._generate_reasons(wx_signals, []),
            "wx_evidence": {
                "message_count": mention_count,
                "messages": [self._summarize_message(m) for m in wx_signals[:5]],
                "sentiment_breakdown": {
                    "bullish": bullish_count,
                    "neutral": len(sentiments) - bullish_count - bearish_count,
                    "bearish": bearish_count,
                },
            },
            "wx_mention_count": mention_count,
            "wx_sentiment_score": sentiment_score,
            "wx_signal_strength": confidence,
            "selection_date": datetime.now(),
            "status": "active",
        }

        return pick

    def _generate_wx_plus_external_pick(
        self,
        ticker: str,
        wx_signals: List[Dict[str, Any]],
        external_signals: List[Dict[str, Any]],
        min_confidence: float,
    ) -> Optional[Dict[str, Any]]:
        """Generate a WeChat + External stock pick."""
        # CRITICAL: Ensure WeChat weight >= 0.6
        wx_weight = 0.65
        external_weight = 0.25
        fundamental_weight = 0.10

        # Calculate signals
        wx_score = self._calculate_wx_score(wx_signals)
        external_score = self._calculate_external_score(external_signals)

        # Combined score
        combined_score = wx_weight * wx_score + external_weight * external_score

        if combined_score < min_confidence:
            return None

        # Determine action
        action = "BUY" if combined_score > 0 else "SELL"

        pick = {
            "ticker": ticker,
            "company_name": self._get_company_name(ticker),
            "action": action,
            "confidence_score": abs(combined_score),
            "reasons": self._generate_reasons(wx_signals, external_signals),
            "wx_evidence": self._build_wx_evidence(wx_signals),
            "wx_weight": wx_weight,
            "wx_mention_count": len(wx_signals),
            "wx_sentiment_score": wx_score,
            "external_evidence": self._build_external_evidence(external_signals),
            "external_weight": external_weight,
            "external_source_count": len(external_signals),
            "external_sentiment_score": external_score,
            "combined_signal_strength": abs(combined_score),
            "selection_date": datetime.now(),
            "status": "active",
        }

        return pick

    def _calculate_wx_confidence(
        self, signals: List[Dict[str, Any]], sentiment_score: float
    ) -> float:
        """Calculate confidence for WeChat signals."""
        # Factors: mention count, sentiment consensus, source quality
        mention_count = len(signals)
        avg_quality = sum(
            s.get("metadata", {}).get("quality_score", 0.5) for s in signals
        ) / len(signals)

        confidence = (
            0.3 * min(mention_count / 10, 1.0)  # More mentions = higher
            + 0.4 * abs(sentiment_score)  # Strong sentiment = higher
            + 0.3 * avg_quality  # High quality = higher
        )

        return min(confidence, 1.0)

    def _calculate_wx_score(self, signals: List[Dict[str, Any]]) -> float:
        """Calculate WeChat signal score (-1 to 1)."""
        if not signals:
            return 0.0

        sentiments = [s.get("metadata", {}).get("sentiment") for s in signals]
        bullish = sum(1 for s in sentiments if s == "bullish")
        bearish = sum(1 for s in sentiments if s == "bearish")

        return (bullish - bearish) / len(sentiments)

    def _calculate_external_score(self, signals: List[Dict[str, Any]]) -> float:
        """Calculate external signal score (-1 to 1)."""
        if not signals:
            return 0.0

        scores = [s.get("sentiment_score", 0.0) for s in signals]
        return sum(scores) / len(scores)

    def _get_company_name(self, ticker: str) -> str:
        """Get company name for ticker."""
        # TODO: Implement ticker to company name mapping
        return f"Company_{ticker}"

    def _generate_reasons(
        self, wx_signals: List[Dict[str, Any]], external_signals: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate reasons for the pick."""
        reasons = []

        # WeChat reason
        if wx_signals:
            reasons.append(
                f"WeChat群内{len(wx_signals)}条消息提及，情绪积极"
            )

        # External reason
        if external_signals:
            reasons.append(
                f"{len(external_signals)}个外部信息源确认，包括新闻和社交媒体"
            )

        # Add generic reasons (TODO: make more specific)
        reasons.append("市场关注度提升，讨论热度增加")

        return reasons[:3]  # Top 3 reasons

    def _summarize_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize a message for evidence."""
        return {
            "sender": msg.get("sender"),
            "content": msg.get("content", "")[:200],  # First 200 chars
            "timestamp": msg.get("timestamp"),
            "sentiment": msg.get("metadata", {}).get("sentiment"),
        }

    def _build_wx_evidence(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build WeChat evidence structure."""
        return {
            "message_count": len(signals),
            "messages": [self._summarize_message(m) for m in signals[:5]],
        }

    def _build_external_evidence(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build external evidence structure."""
        return {
            "source_count": len(signals),
            "sources": [s.get("source") for s in signals],
        }
