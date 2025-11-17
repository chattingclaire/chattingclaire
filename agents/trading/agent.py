"""Trading Agent - Execute trades and provide dashboard."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from agents.base_agent import BaseAgent


class TradingAgent(BaseAgent):
    """
    Agent 6: Trading Agent

    Executes paper trades and provides dashboard visualizations.
    """

    def __init__(self, initial_capital: float = 100000):
        super().__init__(
            agent_name="trading_agent",
            prompt_file="trading_agent.md",
        )

        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # ticker -> shares
        self.trade_history = []

        # Trading constants
        self.SLIPPAGE = 0.001  # 0.1%
        self.COMMISSION_RATE = 0.001  # 0.1%

    def run(
        self,
        mode: str = "execute",  # execute, monitor, backtest
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run trading agent in different modes.

        Args:
            mode: Operation mode
                - execute: Execute pending strategies
                - monitor: Monitor open positions
                - backtest: Run backtest

        Returns:
            Execution results
        """
        logger.info(f"Running trading agent in {mode} mode")

        if mode == "execute":
            return self._execute_pending_strategies()
        elif mode == "monitor":
            return self._monitor_positions()
        elif mode == "backtest":
            return self._run_backtest(**kwargs)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _execute_pending_strategies(self) -> Dict[str, Any]:
        """Execute pending strategy recommendations."""
        # Get pending strategies from database
        pending = self._get_pending_strategies()

        logger.info(f"Found {len(pending)} pending strategies")

        results = {
            "total_pending": len(pending),
            "executed": 0,
            "skipped": 0,
            "errors": [],
        }

        for strategy in pending:
            try:
                ticker = strategy["ticker"]
                action = strategy["action"]
                position_size_pct = strategy["position_size_pct"]

                # Calculate shares
                portfolio_value = self.get_portfolio_value()
                position_value = portfolio_value * position_size_pct
                current_price = self._get_current_price(ticker)
                shares = int(position_value / current_price)

                if shares < 1:
                    logger.warning(f"Skipping {ticker} - position too small")
                    results["skipped"] += 1
                    continue

                # Check risk constraints
                if not self._check_risk_constraints(strategy, shares):
                    logger.warning(f"Skipping {ticker} - risk constraints violated")
                    results["skipped"] += 1
                    continue

                # Execute trade
                trade = self.execute_order(
                    ticker=ticker,
                    action=action,
                    shares=shares,
                    order_type="market",
                )

                if trade:
                    # Update strategy status
                    self.db.update(
                        "strategy_outputs",
                        {"status": "executed"},
                        {"id": strategy["id"]},
                    )
                    results["executed"] += 1
                    logger.info(f"Executed: {action} {shares} {ticker}")

            except Exception as e:
                logger.error(f"Error executing strategy: {e}")
                results["errors"].append({"strategy": strategy, "error": str(e)})

        logger.info(f"Execution complete: {results}")
        return results

    def execute_order(
        self,
        ticker: str,
        action: str,
        shares: int,
        order_type: str = "market",
        limit_price: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute a trade order (paper trading)."""
        try:
            # Get current price
            current_price = self._get_current_price(ticker)

            # Apply slippage
            if action == "BUY":
                execution_price = current_price * (1 + self.SLIPPAGE)
            else:  # SELL
                execution_price = current_price * (1 - self.SLIPPAGE)

            # Calculate costs
            total_value = execution_price * shares
            commission = total_value * self.COMMISSION_RATE

            # Validate order
            if action == "BUY":
                if self.cash < (total_value + commission):
                    logger.error(f"Insufficient cash for {ticker}")
                    return None
            else:  # SELL
                if ticker not in self.positions or self.positions[ticker] < shares:
                    logger.error(f"Insufficient shares for {ticker}")
                    return None

            # Execute
            if action == "BUY":
                self.cash -= (total_value + commission)
                self.positions[ticker] = self.positions.get(ticker, 0) + shares
            else:  # SELL
                self.cash += (total_value - commission)
                self.positions[ticker] -= shares
                if self.positions[ticker] == 0:
                    del self.positions[ticker]

            # Record trade
            trade = {
                "ticker": ticker,
                "action": action,
                "shares": shares,
                "price": execution_price,
                "total_value": total_value,
                "commission": commission,
                "slippage": abs(execution_price - current_price) * shares,
                "executed_at": datetime.now(),
                "portfolio_value_before": self.get_portfolio_value()
                + (total_value + commission if action == "BUY" else -(total_value - commission)),
                "portfolio_value_after": self.get_portfolio_value(),
                "cash_balance": self.cash,
            }

            self.trade_history.append(trade)

            # Write to database
            self.db.insert("executed_trades", trade)

            logger.info(
                f"Executed {action} {shares} {ticker} @ ${execution_price:.2f}"
            )

            return trade

        except Exception as e:
            logger.error(f"Error executing order: {e}")
            return None

    def _monitor_positions(self) -> Dict[str, Any]:
        """Monitor open positions and check stop-loss/take-profit."""
        results = {
            "total_positions": len(self.positions),
            "alerts": [],
            "exits": [],
        }

        for ticker, shares in list(self.positions.items()):
            try:
                # Get position details
                position_info = self._get_position_info(ticker)
                current_price = self._get_current_price(ticker)

                # Calculate P&L
                entry_price = position_info.get("entry_price", current_price)
                unrealized_pnl = (current_price - entry_price) * shares
                pnl_pct = (current_price - entry_price) / entry_price

                # Check stop loss
                stop_loss = position_info.get("stop_loss")
                if stop_loss and current_price <= stop_loss:
                    logger.warning(f"Stop loss triggered for {ticker}")
                    trade = self.execute_order(ticker, "SELL", shares)
                    if trade:
                        results["exits"].append(
                            {"ticker": ticker, "reason": "stop_loss", "trade": trade}
                        )
                    continue

                # Check take profit
                take_profit = position_info.get("take_profit")
                if take_profit and current_price >= take_profit:
                    logger.info(f"Take profit triggered for {ticker}")
                    trade = self.execute_order(ticker, "SELL", shares)
                    if trade:
                        results["exits"].append(
                            {"ticker": ticker, "reason": "take_profit", "trade": trade}
                        )
                    continue

                # Generate alerts
                if pnl_pct < -0.05:
                    results["alerts"].append(
                        {
                            "ticker": ticker,
                            "type": "large_loss",
                            "message": f"{ticker} down {pnl_pct*100:.1f}%",
                        }
                    )

            except Exception as e:
                logger.error(f"Error monitoring {ticker}: {e}")

        return results

    def _run_backtest(
        self,
        strategy_name: str,
        start_date: str,
        end_date: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Run backtest for a strategy."""
        # TODO: Implement comprehensive backtesting
        logger.info(f"Backtesting {strategy_name} from {start_date} to {end_date}")

        return {
            "strategy_name": strategy_name,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": self.initial_capital,
            "final_capital": 0,  # TODO
            "total_return": 0,  # TODO
            "sharpe_ratio": 0,  # TODO
            "max_drawdown": 0,  # TODO
        }

    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value."""
        positions_value = sum(
            shares * self._get_current_price(ticker)
            for ticker, shares in self.positions.items()
        )
        return self.cash + positions_value

    def _get_pending_strategies(self) -> List[Dict[str, Any]]:
        """Get pending strategies from database."""
        # TODO: Query database
        return []

    def _get_position_info(self, ticker: str) -> Dict[str, Any]:
        """Get detailed position information."""
        # TODO: Query from database
        return {}

    def _get_current_price(self, ticker: str) -> float:
        """Get current market price."""
        # TODO: Fetch from market data API
        return 100.00  # Placeholder

    def _check_risk_constraints(
        self, strategy: Dict[str, Any], shares: int
    ) -> bool:
        """Check if trade violates risk constraints."""
        # TODO: Implement comprehensive risk checks
        return True

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display."""
        portfolio_value = self.get_portfolio_value()
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital

        return {
            "portfolio": {
                "value": portfolio_value,
                "cash": self.cash,
                "positions_value": portfolio_value - self.cash,
                "total_return": total_return,
                "total_return_pct": total_return * 100,
            },
            "positions": [
                {
                    "ticker": ticker,
                    "shares": shares,
                    "current_price": self._get_current_price(ticker),
                    "value": shares * self._get_current_price(ticker),
                }
                for ticker, shares in self.positions.items()
            ],
            "recent_trades": self.trade_history[-10:],
            "metrics": {
                "total_trades": len(self.trade_history),
                "open_positions": len(self.positions),
            },
        }
