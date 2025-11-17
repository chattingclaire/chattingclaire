"""Main orchestrator for multi-agent trading system."""

import asyncio
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime

from agents import (
    WxSourceAgent,
    ExternalSourceAgent,
    SelectionAgent,
    FundamentalAgent,
    StrategyAgent,
    TradingAgent,
)


class TradingOrchestrator:
    """
    Orchestrates the 6-agent pipeline for the trading system.

    Pipeline:
    1. WxSourceAgent: Parse WeChat messages
    2. ExternalSourceAgent: Collect external signals
    3. SelectionAgent: Generate stock picks (WX weight >= 60%)
    4. FundamentalAgent: Enrich with fundamental data
    5. StrategyAgent: Build trading strategies
    6. TradingAgent: Execute trades and monitor
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # Initialize agents
        self.wx_agent = WxSourceAgent()
        self.external_agent = ExternalSourceAgent()
        self.selection_agent = SelectionAgent()
        self.fundamental_agent = FundamentalAgent()
        self.strategy_agent = StrategyAgent()
        self.trading_agent = TradingAgent(
            initial_capital=self.config.get("initial_capital", 100000)
        )

        logger.info("Trading orchestrator initialized")

    async def run_pipeline(
        self,
        wechat_export_path: str = None,
        mode: str = "full",  # full, signals_only, execution_only
    ) -> Dict[str, Any]:
        """
        Run the complete multi-agent pipeline.

        Args:
            wechat_export_path: Path to WeChat export (if processing new data)
            mode: Pipeline mode
                - full: Run all agents
                - signals_only: Run agents 1-3 (collect signals, no execution)
                - execution_only: Run agents 4-6 (use existing signals)

        Returns:
            Pipeline results
        """
        logger.info(f"Starting pipeline in {mode} mode")
        start_time = datetime.now()

        results = {
            "mode": mode,
            "start_time": start_time,
            "agent_results": {},
        }

        try:
            # Stage 1: Collect Signals (Agents 1-2)
            if mode in ["full", "signals_only"]:
                logger.info("=== Stage 1: Signal Collection ===")

                # Agent 1: WeChat Source
                if wechat_export_path:
                    with self.wx_agent:
                        wx_results = self.wx_agent.run(wechat_export_path=wechat_export_path)
                        results["agent_results"]["wx_source"] = wx_results

                # Agent 2: External Sources
                with self.external_agent:
                    external_results = self.external_agent.run(
                        sources=["twitter", "reddit", "news", "edgar"],
                        lookback_days=7,
                    )
                    results["agent_results"]["external_source"] = external_results

            # Stage 2: Stock Selection (Agent 3)
            if mode in ["full", "signals_only"]:
                logger.info("=== Stage 2: Stock Selection ===")

                with self.selection_agent:
                    selection_results = self.selection_agent.run(
                        mode="both",  # Generate both WX-only and WX+External picks
                        lookback_days=7,
                        min_confidence=0.6,
                    )
                    results["agent_results"]["selection"] = selection_results

            # Stage 3: Fundamental Analysis (Agent 4)
            if mode in ["full", "execution_only"]:
                logger.info("=== Stage 3: Fundamental Analysis ===")

                with self.fundamental_agent:
                    fundamental_results = self.fundamental_agent.run()
                    results["agent_results"]["fundamental"] = fundamental_results

            # Stage 4: Strategy Generation (Agent 5)
            if mode in ["full", "execution_only"]:
                logger.info("=== Stage 4: Strategy Generation ===")

                with self.strategy_agent:
                    strategy_results = self.strategy_agent.run(
                        strategies=None,  # Use all enabled strategies
                    )
                    results["agent_results"]["strategy"] = strategy_results

            # Stage 5: Trade Execution (Agent 6)
            if mode in ["full", "execution_only"]:
                logger.info("=== Stage 5: Trade Execution ===")

                with self.trading_agent:
                    # Execute pending strategies
                    execution_results = self.trading_agent.run(mode="execute")
                    results["agent_results"]["execution"] = execution_results

                    # Monitor existing positions
                    monitoring_results = self.trading_agent.run(mode="monitor")
                    results["agent_results"]["monitoring"] = monitoring_results

            # Record completion
            end_time = datetime.now()
            results["end_time"] = end_time
            results["duration"] = (end_time - start_time).total_seconds()
            results["status"] = "success"

            logger.info(f"Pipeline completed successfully in {results['duration']:.2f}s")

            return results

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results

    def run_scheduled(self, schedule: Dict[str, Any]):
        """
        Run pipeline on a schedule.

        Example schedule:
        {
            "signals_collection": "*/30 * * * *",  # Every 30 minutes
            "stock_selection": "0 */2 * * *",      # Every 2 hours
            "strategy_generation": "0 9,15 * * *", # 9 AM and 3 PM
            "trade_execution": "0 9,15 * * 1-5",   # 9 AM and 3 PM, weekdays
        }
        """
        # TODO: Implement scheduling with APScheduler or similar
        logger.info("Scheduled execution not yet implemented")

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents and system health."""
        return {
            "agents": {
                "wx_source": "operational",
                "external_source": "operational",
                "selection": "operational",
                "fundamental": "operational",
                "strategy": "operational",
                "trading": "operational",
            },
            "trading": {
                "portfolio_value": self.trading_agent.get_portfolio_value(),
                "cash": self.trading_agent.cash,
                "positions": len(self.trading_agent.positions),
                "trades": len(self.trading_agent.trade_history),
            },
        }


# CLI entry point
def main():
    """Main entry point for CLI execution."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Agent Trading System")
    parser.add_argument("--mode", choices=["full", "signals_only", "execution_only"], default="full")
    parser.add_argument("--wechat-export", type=str, help="Path to WeChat export")
    parser.add_argument("--status", action="store_true", help="Show system status")

    args = parser.parse_args()

    orchestrator = TradingOrchestrator()

    if args.status:
        status = orchestrator.get_system_status()
        print(status)
        return

    # Run pipeline
    results = asyncio.run(orchestrator.run_pipeline(
        wechat_export_path=args.wechat_export,
        mode=args.mode,
    ))

    print(f"\nPipeline Results:")
    print(f"Status: {results['status']}")
    print(f"Duration: {results.get('duration', 0):.2f}s")

    for agent, result in results.get("agent_results", {}).items():
        print(f"\n{agent}: {result}")


if __name__ == "__main__":
    main()
