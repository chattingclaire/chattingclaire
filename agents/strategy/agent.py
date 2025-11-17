"""Strategy Agent - Build trading strategies from signals and fundamentals."""

import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

from agents.base_agent import BaseAgent


class StrategyAgent(BaseAgent):
    """
    Agent 5: Strategy Agent

    Builds trading strategies based on WeChat signals, external data, and fundamentals.
    Ensures WeChat weight >= 60%.
    """

    def __init__(self):
        super().__init__(
            agent_name="strategy_agent",
            prompt_file="strategy_agent.md",
        )

        # Load strategy configuration
        with open("config/strategy_config.yaml") as f:
            self.strategy_config = yaml.safe_load(f)["strategy"]

    def run(
        self,
        strategies: List[str] = None,
        tickers: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate trading strategies.

        Args:
            strategies: List of strategy types to run (if None, run all enabled)
            tickers: Specific tickers to analyze (if None, get from recent picks)

        Returns:
            Strategy generation results
        """
        logger.info(f"Running strategy agent")

        # Get enabled strategies
        if strategies is None:
            strategies = [
                name
                for name, cfg in self.strategy_config["strategies"].items()
                if isinstance(cfg, dict) and cfg.get("enabled", False)
            ]

        logger.info(f"Running strategies: {strategies}")

        # Get tickers
        if tickers is None:
            tickers = self._get_active_pick_tickers()

        logger.info(f"Analyzing {len(tickers)} tickers")

        results = {
            "total_strategies": 0,
            "by_strategy": {},
            "errors": [],
        }

        for strategy_name in strategies:
            try:
                strategy_outputs = self._run_strategy(strategy_name, tickers)
                results["by_strategy"][strategy_name] = len(strategy_outputs)
                results["total_strategies"] += len(strategy_outputs)

                # Insert into database
                if strategy_outputs:
                    self.db.insert_many("strategy_outputs", strategy_outputs)
                    logger.info(
                        f"Generated {len(strategy_outputs)} outputs for {strategy_name}"
                    )

            except Exception as e:
                logger.error(f"Error running strategy {strategy_name}: {e}")
                results["errors"].append({"strategy": strategy_name, "error": str(e)})

        logger.info(f"Strategy generation complete: {results}")
        return results

    def _get_active_pick_tickers(self) -> List[str]:
        """Get tickers from active stock picks."""
        # TODO: Query database for active picks
        return []

    def _run_strategy(
        self, strategy_name: str, tickers: List[str]
    ) -> List[Dict[str, Any]]:
        """Run a specific strategy on tickers."""
        strategy_outputs = []

        for ticker in tickers:
            try:
                # Get data for ticker
                pick_data = self._get_pick_data(ticker)
                fundamental_data = self._get_fundamental_data(ticker)

                if not pick_data:
                    continue

                # Generate strategy based on type
                if strategy_name == "wechat_sentiment_momentum":
                    output = self._wechat_sentiment_momentum(
                        ticker, pick_data, fundamental_data
                    )
                elif strategy_name == "event_driven":
                    output = self._event_driven(ticker, pick_data, fundamental_data)
                elif strategy_name == "value_momentum_combo":
                    output = self._value_momentum_combo(
                        ticker, pick_data, fundamental_data
                    )
                elif strategy_name == "multi_source_weighted":
                    output = self._multi_source_weighted(
                        ticker, pick_data, fundamental_data
                    )
                else:
                    logger.warning(f"Unknown strategy: {strategy_name}")
                    continue

                if output:
                    strategy_outputs.append(output)

            except Exception as e:
                logger.error(f"Error processing {ticker} in {strategy_name}: {e}")

        return strategy_outputs

    def _wechat_sentiment_momentum(
        self,
        ticker: str,
        pick_data: Dict[str, Any],
        fundamental_data: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """WeChat sentiment momentum strategy."""
        wx_sentiment = pick_data.get("wx_sentiment_score", 0)
        wx_mentions = pick_data.get("wx_mention_count", 0)

        # Check entry criteria
        if wx_mentions < 3 or wx_sentiment < 0.6:
            return None

        # Calculate position size
        position_size = self._calculate_position_size(
            confidence=pick_data.get("confidence_score", 0.7)
        )

        # Calculate risk levels
        current_price = self._get_current_price(ticker)
        risk_config = self.strategy_config["risk"]

        return {
            "strategy_name": "wechat_sentiment_momentum",
            "strategy_type": "sentiment_momentum",
            "ticker": ticker,
            "action": pick_data.get("action", "BUY"),
            "recommended_price": current_price,
            "position_size_pct": position_size,
            "stop_loss": current_price * (1 - risk_config["stop_loss_pct"]),
            "take_profit": current_price * (1 + risk_config["take_profit_pct"]),
            "max_loss_pct": risk_config["stop_loss_pct"],
            "max_gain_pct": risk_config["take_profit_pct"],
            "signal_breakdown": {
                "wechat": wx_sentiment,
                "external": 0,
                "fundamental": 0,
                "technical": 0,
            },
            "wechat_signal_weight": 1.0,
            "confidence_score": pick_data.get("confidence_score", 0.7),
            "strategy_params": {
                "lookback_days": 7,
                "min_mentions": 3,
                "sentiment_threshold": 0.6,
            },
            "status": "pending",
            "created_at": datetime.now(),
        }

    def _event_driven(
        self,
        ticker: str,
        pick_data: Dict[str, Any],
        fundamental_data: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Event-driven strategy."""
        # TODO: Implement event detection and strategy
        return None

    def _value_momentum_combo(
        self,
        ticker: str,
        pick_data: Dict[str, Any],
        fundamental_data: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Value-momentum combination strategy."""
        # TODO: Implement value-momentum strategy
        return None

    def _multi_source_weighted(
        self,
        ticker: str,
        pick_data: Dict[str, Any],
        fundamental_data: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Multi-source weighted strategy."""
        weights = self.strategy_config["signal_weights"]

        # CRITICAL: Ensure WeChat >= 0.6
        assert weights["wechat"] >= 0.6, "WeChat weight must be >= 0.6"

        # Calculate weighted signal
        wx_score = pick_data.get("wx_sentiment_score", 0) * weights["wechat"]
        ext_score = pick_data.get("external_sentiment_score", 0) * weights["external"]
        # TODO: Add fundamental and technical signals

        combined_score = wx_score + ext_score

        if abs(combined_score) < 0.6:
            return None

        current_price = self._get_current_price(ticker)
        position_size = self._calculate_position_size(abs(combined_score))

        return {
            "strategy_name": "multi_source_weighted",
            "strategy_type": "multi_source",
            "ticker": ticker,
            "action": "BUY" if combined_score > 0 else "SELL",
            "recommended_price": current_price,
            "position_size_pct": position_size,
            "signal_breakdown": {
                "wechat": wx_score,
                "external": ext_score,
                "fundamental": 0,
                "technical": 0,
            },
            "wechat_signal_weight": weights["wechat"],
            "external_signal_weight": weights["external"],
            "confidence_score": abs(combined_score),
            "status": "pending",
            "created_at": datetime.now(),
        }

    def _get_pick_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get stock pick data for ticker."""
        # TODO: Query from database
        return None

    def _get_fundamental_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get fundamental data for ticker."""
        # TODO: Query from database
        return None

    def _get_current_price(self, ticker: str) -> float:
        """Get current market price for ticker."""
        # TODO: Fetch from market data API
        return 100.00  # Placeholder

    def _calculate_position_size(self, confidence: float) -> float:
        """Calculate position size based on confidence and risk config."""
        risk_config = self.strategy_config["risk"]
        capital_config = self.strategy_config["capital"]

        base_size = risk_config["max_position_size"]
        position_size = base_size * confidence

        return min(position_size, risk_config["max_position_size"])
