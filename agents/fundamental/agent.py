"""Fundamental Agent - Enrich stock picks with fundamental data."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from agents.base_agent import BaseAgent


class FundamentalAgent(BaseAgent):
    """
    Agent 4: Fundamental Agent

    Enriches stock picks with comprehensive fundamental analysis.
    """

    def __init__(self):
        super().__init__(
            agent_name="fundamental_agent",
            prompt_file="fundamental_agent.md",
        )

    def run(
        self,
        tickers: List[str] = None,
        force_update: bool = False,
    ) -> Dict[str, Any]:
        """
        Enrich tickers with fundamental data.

        Args:
            tickers: List of tickers to analyze (if None, get from recent picks)
            force_update: Force update even if data exists

        Returns:
            Processing results
        """
        logger.info(f"Running fundamental analysis")

        # Get tickers from recent picks if not specified
        if tickers is None:
            tickers = self._get_recent_pick_tickers()

        logger.info(f"Analyzing {len(tickers)} tickers")

        results = {
            "total_tickers": len(tickers),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        for ticker in tickers:
            try:
                # Check if data exists and is recent
                if not force_update and self._has_recent_data(ticker):
                    logger.info(f"Skipping {ticker} - recent data exists")
                    continue

                # Fetch and process fundamental data
                fundamental_data = self._analyze_ticker(ticker)

                if fundamental_data:
                    # Upsert to database
                    self.db.insert("stock_fundamentals", fundamental_data)
                    results["successful"] += 1
                    logger.info(f"Successfully analyzed {ticker}")
                else:
                    results["failed"] += 1

            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                results["failed"] += 1
                results["errors"].append({"ticker": ticker, "error": str(e)})

        logger.info(f"Fundamental analysis complete: {results}")
        return results

    def _get_recent_pick_tickers(self, days: int = 7) -> List[str]:
        """Get tickers from recent stock picks."""
        # Query both pick tables
        query_wx = """
            SELECT DISTINCT ticker FROM stock_picks_wx_only
            WHERE selection_date >= NOW() - INTERVAL '%s days'
            AND status = 'active'
        """
        query_combined = """
            SELECT DISTINCT ticker FROM stock_picks_wx_plus_external
            WHERE selection_date >= NOW() - INTERVAL '%s days'
            AND status = 'active'
        """

        # Simplified: return empty for now (TODO: implement proper query)
        return []

    def _has_recent_data(self, ticker: str, max_age_days: int = 1) -> bool:
        """Check if we have recent fundamental data for ticker."""
        query = """
            SELECT COUNT(*) as count FROM stock_fundamentals
            WHERE ticker = %s
            AND data_date >= NOW() - INTERVAL '%s days'
        """
        # Simplified: return False for now
        return False

    def _analyze_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Perform comprehensive fundamental analysis on a ticker.
        """
        logger.info(f"Analyzing {ticker}")

        try:
            # Fetch data from multiple sources
            company_info = self._fetch_company_info(ticker)
            financials = self._fetch_financials(ticker)
            valuation = self._calculate_valuation(ticker, financials)
            dcf = self._calculate_dcf(ticker, financials)
            analyst_data = self._fetch_analyst_data(ticker)
            news = self._fetch_recent_news(ticker)

            # Build fundamental data structure
            fundamental_data = {
                "ticker": ticker,
                "company_name": company_info.get("name"),
                "sector": company_info.get("sector"),
                "industry": company_info.get("industry"),
                "gics_sector": company_info.get("gics_sector"),
                "gics_industry": company_info.get("gics_industry"),
                "business_summary": company_info.get("description"),
                "business_segments": company_info.get("segments"),
                "market_cap": company_info.get("market_cap"),
                # Financials
                "revenue": financials.get("revenue"),
                "net_income": financials.get("net_income"),
                "gross_margin": financials.get("gross_margin"),
                "operating_margin": financials.get("operating_margin"),
                "net_margin": financials.get("net_margin"),
                "roe": financials.get("roe"),
                "roa": financials.get("roa"),
                # Valuation
                "pe_ratio": valuation.get("pe"),
                "pb_ratio": valuation.get("pb"),
                "ps_ratio": valuation.get("ps"),
                "peg_ratio": valuation.get("peg"),
                "ev_ebitda": valuation.get("ev_ebitda"),
                "dividend_yield": valuation.get("dividend_yield"),
                # DCF
                "dcf_fair_value": dcf.get("fair_value"),
                "dcf_assumptions": dcf.get("assumptions"),
                # Latest filings
                "latest_10k_date": None,  # TODO
                "latest_10q_date": None,  # TODO
                "latest_earnings_date": None,  # TODO
                "earnings_transcript": None,  # TODO
                # Analyst data
                "analyst_ratings": analyst_data.get("ratings"),
                "price_targets": analyst_data.get("price_targets"),
                # News
                "recent_news": news,
                "recent_events": [],  # TODO
                "data_date": datetime.now().date(),
                "metadata": {
                    "data_sources": ["yahoo", "openbb"],  # TODO: track actual sources
                    "data_quality": 0.85,  # TODO: calculate
                },
            }

            return fundamental_data

        except Exception as e:
            logger.error(f"Error in _analyze_ticker for {ticker}: {e}")
            return None

    def _fetch_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch basic company information using Tushare + AKShare."""
        from tools.datasources.tushare_tool import tushare_api
        from tools.datasources.akshare_tool import akshare_api

        try:
            # 判断市场
            if len(ticker) == 6 and ticker.isdigit():
                # A股/港股 - 使用 Tushare + AKShare
                ts_code = tushare_api.normalize_ticker(ticker)

                # Tushare: 基本信息
                basic = tushare_api.get_stock_basic(ts_code)
                company = tushare_api.get_company_info(ts_code)

                # AKShare: 补充实时信息
                realtime = akshare_api.get_stock_individual_info(ticker)

                return {
                    "name": basic.get("name") or company.get("chairman"),
                    "sector": basic.get("industry"),
                    "industry": basic.get("industry"),
                    "description": company.get("introduction"),
                    "market_cap": realtime.get("总市值"),
                    "gics_sector": basic.get("industry"),
                    "gics_industry": basic.get("industry"),
                }
            else:
                # 美股 - 使用 yfinance
                import yfinance as yf
                stock = yf.Ticker(ticker)
                info = stock.info

                return {
                    "name": info.get("longName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "description": info.get("longBusinessSummary"),
                    "market_cap": info.get("marketCap"),
                    "gics_sector": info.get("sector"),
                    "gics_industry": info.get("industry"),
                }
        except Exception as e:
            logger.error(f"Error fetching company info: {e}")
            return {
                "name": f"Company {ticker}",
                "sector": "Unknown",
                "industry": "Unknown",
                "description": "",
                "market_cap": 0,
            }

    def _fetch_financials(self, ticker: str) -> Dict[str, Any]:
        """Fetch financial metrics using Tushare."""
        from tools.datasources.tushare_tool import tushare_api

        try:
            if len(ticker) == 6 and ticker.isdigit():
                # A股 - 使用 Tushare
                ts_code = tushare_api.normalize_ticker(ticker)

                # 获取最新财务数据
                income = tushare_api.get_income_statement(ts_code)
                indicators = tushare_api.get_financial_indicators(ts_code)

                return {
                    "revenue": income.get("revenue"),
                    "net_income": income.get("n_income"),
                    "gross_margin": indicators.get("grossprofit_margin"),
                    "operating_margin": indicators.get("op_income_margin"),
                    "net_margin": indicators.get("netprofit_margin"),
                    "roe": indicators.get("roe"),
                    "roa": indicators.get("roa"),
                }
            else:
                # 美股 - 使用 yfinance
                import yfinance as yf
                stock = yf.Ticker(ticker)
                info = stock.info

                return {
                    "revenue": info.get("totalRevenue"),
                    "net_income": info.get("netIncome"),
                    "gross_margin": info.get("grossMargins"),
                    "operating_margin": info.get("operatingMargins"),
                    "net_margin": info.get("profitMargins"),
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                }
        except Exception as e:
            logger.error(f"Error fetching financials: {e}")
            return {
                "revenue": 0,
                "net_income": 0,
                "gross_margin": 0,
                "operating_margin": 0,
                "net_margin": 0,
                "roe": 0,
                "roa": 0,
            }

    def _calculate_valuation(
        self, ticker: str, financials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate valuation metrics."""
        # TODO: Implement proper valuation calculations
        return {
            "pe": 25.0,
            "pb": 5.0,
            "ps": 8.0,
            "peg": 2.0,
            "ev_ebitda": 18.0,
            "dividend_yield": 0.015,
        }

    def _calculate_dcf(
        self, ticker: str, financials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate DCF fair value."""
        # TODO: Implement DCF model
        return {
            "fair_value": 150.00,
            "assumptions": {
                "wacc": 0.10,
                "terminal_growth": 0.03,
                "fcf_projections": [1000, 1100, 1210, 1330, 1460],
            },
        }

    def _fetch_analyst_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch analyst ratings and price targets."""
        # TODO: Implement analyst data fetching
        return {
            "ratings": {
                "strong_buy": 10,
                "buy": 8,
                "hold": 3,
                "sell": 1,
                "strong_sell": 0,
            },
            "price_targets": {
                "high": 200.00,
                "average": 175.00,
                "low": 150.00,
                "median": 178.00,
            },
        }

    def _fetch_recent_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch recent news using AKShare."""
        from tools.datasources.akshare_tool import akshare_api

        try:
            if len(ticker) == 6 and ticker.isdigit():
                # A股 - 使用 AKShare 获取新闻
                news = akshare_api.get_stock_news(ticker, limit=20)
                return news
            else:
                # 美股 - TODO: 实现美股新闻
                return []
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
