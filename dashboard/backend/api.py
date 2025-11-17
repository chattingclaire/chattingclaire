"""FastAPI Dashboard Backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from database import get_db
from agents import TradingAgent
from memory import ContextManager

# Import search API router
from .search_api import router as search_router

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Trading System Dashboard",
    description="Dashboard API for WeChat-driven trading system",
    version="1.0.0",
)

# Include search API routes
app.include_router(search_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = get_db()
context_manager = ContextManager()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "Multi-Agent Trading System",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/api/dashboard/overview")
async def get_overview():
    """
    Dashboard overview with key metrics.
    """
    try:
        # Get portfolio metrics
        portfolio = _get_portfolio_metrics()

        # Get recent trades
        recent_trades = _get_recent_trades(limit=10)

        # Get open positions
        open_positions = _get_open_positions()

        # Get daily P&L
        daily_pnl = _calculate_daily_pnl()

        # Get alerts
        alerts = _get_active_alerts()

        return {
            "portfolio": portfolio,
            "recent_trades": recent_trades,
            "open_positions": open_positions,
            "daily_pnl": daily_pnl,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error in get_overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/wechat")
async def get_wechat_panel(days: int = 30):
    """
    WeChat sentiment and activity panel.
    """
    try:
        return {
            "sentiment_trend": _get_wx_sentiment_trend(days),
            "top_mentioned_stocks": _get_wx_top_stocks(limit=10),
            "recent_messages": _get_wx_recent_messages(limit=20),
            "hot_topics": _get_wx_hot_topics(),
            "sentiment_by_ticker": _get_wx_sentiment_by_ticker(),
        }
    except Exception as e:
        logger.error(f"Error in get_wechat_panel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/external")
async def get_external_panel():
    """
    External sources panel.
    """
    try:
        return {
            "news_feed": _get_recent_news(limit=20),
            "twitter_trends": _get_twitter_trends(),
            "reddit_hot": _get_reddit_hot_posts(),
            "recent_filings": _get_recent_filings(limit=10),
            "source_breakdown": _get_external_source_breakdown(),
        }
    except Exception as e:
        logger.error(f"Error in get_external_panel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/picks")
async def get_stock_picks(status: str = "active"):
    """
    Stock picks table (WX-only & WX+External).
    """
    try:
        wx_only = db.select(
            "stock_picks_wx_only",
            filters={"status": status},
            limit=20,
            order="selection_date.desc",
        )

        wx_plus_external = db.select(
            "stock_picks_wx_plus_external",
            filters={"status": status},
            limit=20,
            order="selection_date.desc",
        )

        return {
            "wx_only": wx_only,
            "wx_plus_external": wx_plus_external,
            "summary": {
                "total_picks": len(wx_only) + len(wx_plus_external),
                "wx_only_count": len(wx_only),
                "wx_plus_external_count": len(wx_plus_external),
            },
        }
    except Exception as e:
        logger.error(f"Error in get_stock_picks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/fundamentals/{ticker}")
async def get_fundamentals(ticker: str):
    """
    Fundamental data panel for a ticker.
    """
    try:
        fundamentals = db.select(
            "stock_fundamentals",
            filters={"ticker": ticker},
            limit=1,
            order="data_date.desc",
        )

        if not fundamentals:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        fundamental_data = fundamentals[0]

        return {
            "company_info": {
                "name": fundamental_data.get("company_name"),
                "sector": fundamental_data.get("sector"),
                "industry": fundamental_data.get("industry"),
                "market_cap": fundamental_data.get("market_cap"),
            },
            "financial_metrics": {
                "revenue": fundamental_data.get("revenue"),
                "net_income": fundamental_data.get("net_income"),
                "margins": {
                    "gross": fundamental_data.get("gross_margin"),
                    "operating": fundamental_data.get("operating_margin"),
                    "net": fundamental_data.get("net_margin"),
                },
                "roe": fundamental_data.get("roe"),
                "roa": fundamental_data.get("roa"),
            },
            "valuation": {
                "pe_ratio": fundamental_data.get("pe_ratio"),
                "pb_ratio": fundamental_data.get("pb_ratio"),
                "ps_ratio": fundamental_data.get("ps_ratio"),
                "peg_ratio": fundamental_data.get("peg_ratio"),
                "ev_ebitda": fundamental_data.get("ev_ebitda"),
            },
            "dcf_valuation": {
                "fair_value": fundamental_data.get("dcf_fair_value"),
                "assumptions": fundamental_data.get("dcf_assumptions"),
            },
            "analyst_ratings": fundamental_data.get("analyst_ratings"),
            "recent_news": fundamental_data.get("recent_news", []),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_fundamentals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/strategies")
async def get_strategies(status: str = "pending"):
    """
    Strategy recommendations and performance.
    """
    try:
        strategies = db.select(
            "strategy_outputs",
            filters={"status": status} if status != "all" else None,
            limit=50,
            order="created_at.desc",
        )

        return {
            "strategies": strategies,
            "total_count": len(strategies),
        }
    except Exception as e:
        logger.error(f"Error in get_strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/performance")
async def get_performance():
    """
    Portfolio performance and equity curve.
    """
    try:
        equity_curve = _get_equity_curve()
        metrics = _calculate_performance_metrics()

        return {
            "equity_curve": equity_curve,
            "metrics": metrics,
            "benchmark_comparison": _compare_to_benchmark("SPY"),
        }
    except Exception as e:
        logger.error(f"Error in get_performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/context/{ticker}")
async def get_ticker_context(ticker: str):
    """
    Provide complete context for a ticker to the chat agent.
    """
    try:
        context = context_manager.get_ticker_context(ticker)
        return context
    except Exception as e:
        logger.error(f"Error in get_ticker_context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _get_portfolio_metrics() -> Dict[str, Any]:
    """Get current portfolio metrics."""
    # TODO: Implement
    return {
        "total_value": 125000,
        "cash": 25000,
        "positions_value": 100000,
        "daily_pnl": 2500,
        "daily_pnl_pct": 2.0,
        "total_return": 0.25,
        "total_return_pct": 25.0,
    }


def _get_recent_trades(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent trades."""
    return db.select("executed_trades", limit=limit, order="executed_at.desc")


def _get_open_positions() -> List[Dict[str, Any]]:
    """Get open positions."""
    # TODO: Calculate from executed_trades
    return []


def _calculate_daily_pnl() -> Dict[str, Any]:
    """Calculate daily P&L."""
    # TODO: Implement
    return {"pnl": 2500, "pnl_pct": 2.0}


def _get_active_alerts() -> List[Dict[str, Any]]:
    """Get active alerts."""
    # TODO: Implement alert system
    return []


def _get_wx_sentiment_trend(days: int) -> Dict[str, Any]:
    """Get WeChat sentiment trend."""
    # TODO: Implement
    return {}


def _get_wx_top_stocks(limit: int) -> List[Dict[str, Any]]:
    """Get top mentioned stocks on WeChat."""
    # TODO: Implement
    return []


def _get_wx_recent_messages(limit: int) -> List[Dict[str, Any]]:
    """Get recent WeChat messages."""
    return db.select("wx_raw_messages", limit=limit, order="timestamp.desc")


def _get_wx_hot_topics() -> List[str]:
    """Get hot topics from WeChat."""
    # TODO: Implement topic extraction
    return []


def _get_wx_sentiment_by_ticker() -> Dict[str, float]:
    """Get sentiment breakdown by ticker."""
    # TODO: Implement
    return {}


def _get_recent_news(limit: int) -> List[Dict[str, Any]]:
    """Get recent news."""
    return db.select(
        "external_raw_items",
        filters={"source": "news"},
        limit=limit,
        order="published_at.desc",
    )


def _get_twitter_trends() -> List[Dict[str, Any]]:
    """Get Twitter trends."""
    # TODO: Implement
    return []


def _get_reddit_hot_posts() -> List[Dict[str, Any]]:
    """Get hot Reddit posts."""
    # TODO: Implement
    return []


def _get_recent_filings(limit: int) -> List[Dict[str, Any]]:
    """Get recent SEC filings."""
    return db.select(
        "external_raw_items",
        filters={"source": "edgar"},
        limit=limit,
        order="published_at.desc",
    )


def _get_external_source_breakdown() -> Dict[str, int]:
    """Get breakdown of external sources."""
    # TODO: Implement
    return {}


def _get_equity_curve() -> List[Dict[str, Any]]:
    """Get portfolio equity curve."""
    # TODO: Implement
    return []


def _calculate_performance_metrics() -> Dict[str, Any]:
    """Calculate performance metrics."""
    # TODO: Implement
    return {}


def _compare_to_benchmark(benchmark: str) -> Dict[str, Any]:
    """Compare portfolio to benchmark."""
    # TODO: Implement
    return {}


# Run with: uvicorn dashboard.backend.api:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
