# Multi-Agent Trading System (ChattingClaire)

A **production-grade, modular, configurable multi-agent trading system** powered by WeChat as the primary information source, integrated with external data feeds, LLM orchestration, and paper trading simulation.

## 🎯 Overview

This system implements a **6-agent pipeline** that:
- Aggregates WeChat group chats and public account articles (≥60% signal weight)
- Supplements with external sources (Twitter, Reddit, news, SEC filings, etc.)
- Extracts trading signals and picks stocks with evidence-based reasoning
- Enriches with comprehensive fundamental analysis
- Builds and backtests trading strategies
- Executes paper trades and provides real-time dashboards

## 🏗️ Architecture

### 6-Agent Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                  Multi-Agent Trading System                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐
│  Agent 1         │  │  Agent 2         │
│  wx_source       │  │  external_source │
│  (WeChat Parser) │  │  (External APIs) │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Agent 3            │
         │  selection_agent    │
         │  (Stock Picking)    │
         │  WeChat Weight≥60%  │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Agent 4            │
         │  fundamental_agent  │
         │  (Fundamentals)     │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Agent 5            │
         │  strategy_agent     │
         │  (Strategy Builder) │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Agent 6            │
         │  trading_agent      │
         │  (Execution+Dashboard)│
         └─────────────────────┘
```

### Agent Responsibilities

| Agent | Purpose | Input | Output | Weight |
|-------|---------|-------|--------|--------|
| **1. WxSourceAgent** | Parse WeChat messages & articles | WeChat exports (HTML/JSON/DB) | `wx_raw_messages`, `wx_mp_articles` | PRIMARY (≥60%) |
| **2. ExternalSourceAgent** | Collect external signals | Twitter, Reddit, News, SEC | `external_raw_items` | MAX 40% |
| **3. SelectionAgent** | Generate stock picks | Agent 1+2 signals | `stock_picks_wx_only`, `stock_picks_wx_plus_external` | - |
| **4. FundamentalAgent** | Enrich with fundamentals | Stock picks | `stock_fundamentals` | - |
| **5. StrategyAgent** | Build trading strategies | Picks + fundamentals | `strategy_outputs` | - |
| **6. TradingAgent** | Execute & monitor trades | Strategies | `executed_trades`, Dashboard API | - |

## 📊 Database Schema

**Supabase PostgreSQL** with **pgvector** for semantic search.

### Key Tables

- **wx_raw_messages**: WeChat group messages with OCR
- **wx_mp_articles**: WeChat public account articles
- **external_raw_items**: External source data
- **stock_picks_wx_only**: WeChat-only stock picks
- **stock_picks_wx_plus_external**: Combined picks (WX≥60%, Ext≤40%)
- **stock_fundamentals**: Comprehensive fundamental data
- **strategy_outputs**: Generated trading strategies
- **executed_trades**: Paper trading execution log
- **backtest_results**: Strategy backtesting results
- **embeddings**: Vector embeddings for semantic search

See [`database/schema.sql`](database/schema.sql) for full schema.

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.10+
python --version

# PostgreSQL + pgvector (via Supabase)
# Supabase account: https://supabase.com
```

### 2. Installation

```bash
# Clone repository
git clone <repo-url>
cd chattingclaire

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required environment variables:**

```ini
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DATABASE_URL=postgresql://...

# LLM APIs
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key  # For embeddings

# Financial Data (optional)
TUSHARE_TOKEN=your_tushare_token
```

### 4. Database Setup

```bash
# Initialize database schema
psql $DATABASE_URL < database/schema.sql

# Or use Supabase SQL editor to run schema.sql
```

### 5. Run the System

#### Option A: Full Pipeline

```bash
# Run complete pipeline with WeChat export
python orchestrator.py --mode full --wechat-export /path/to/wechat_export
```

#### Option B: Signals Only (No Execution)

```bash
# Collect signals and generate picks only
python orchestrator.py --mode signals_only --wechat-export /path/to/wechat_export
```

#### Option C: Execution Only

```bash
# Execute existing strategies (no new signal collection)
python orchestrator.py --mode execution_only
```

### 6. Start Dashboard

```bash
# Start FastAPI backend
cd dashboard/backend
uvicorn api:app --reload --port 8000

# Dashboard available at: http://localhost:8000/docs
```

## 📁 Project Structure

```
chattingclaire/
├── agents/                      # 6 Agent implementations
│   ├── wx_source/               # Agent 1: WeChat parser
│   ├── external_source/         # Agent 2: External sources
│   ├── selection/               # Agent 3: Stock picker
│   ├── fundamental/             # Agent 4: Fundamentals
│   ├── strategy/                # Agent 5: Strategy builder
│   └── trading/                 # Agent 6: Trading + dashboard
│
├── config/                      # Configuration files
│   ├── model_config.yaml        # LLM model settings
│   ├── strategy_config.yaml     # Strategy parameters
│   └── agent_tools.yaml         # Tool assignments
│
├── database/                    # Database layer
│   ├── schema.sql               # Supabase schema
│   ├── connection.py            # DB connection manager
│   └── models.py                # Data models
│
├── prompts/                     # System prompts
│   └── agents/                  # Agent-specific prompts
│       ├── wx_source_agent.md
│       ├── external_source_agent.md
│       ├── selection_agent.md
│       ├── fundamental_agent.md
│       ├── strategy_agent.md
│       └── trading_agent.md
│
├── tools/                       # Tools & utilities
│   ├── datasources/             # Data source connectors
│   │   ├── wechat_parser.py
│   │   ├── twitter_fetcher.py
│   │   ├── yahoo_tool.py
│   │   └── tushare_tool.py
│   ├── analysis/                # Analysis tools
│   ├── ocr/                     # OCR tools
│   └── cleaning/                # Text cleaning
│
├── memory/                      # Memory & context
│   ├── context_manager.py       # Context management
│   └── embeddings.py            # Embedding generation
│
├── dashboard/                   # Dashboard
│   ├── backend/
│   │   └── api.py               # FastAPI backend
│   └── frontend/                # Frontend (Streamlit/React)
│
├── orchestrator.py              # Main orchestrator
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🔧 Configuration

### Model Configuration (`config/model_config.yaml`)

```yaml
models:
  primary:
    provider: "anthropic"
    model: "claude-sonnet-4-5-20250929"
    temperature: 0.7
    max_tokens: 8000
    cache_control:
      enabled: true
      type: "persistent"
    kv_cache:
      enabled: true
      max_age: 86400
```

### Strategy Configuration (`config/strategy_config.yaml`)

```yaml
strategy:
  risk:
    tolerance: "balanced"  # conservative | balanced | aggressive
    max_position_size: 0.15  # 15% max per position
    stop_loss_pct: 0.08      # 8% stop loss
    take_profit_pct: 0.20    # 20% take profit

  signal_weights:
    wechat: 0.65       # WeChat (MUST be ≥ 0.6)
    external: 0.20     # External sources (MAX 0.4)
    fundamental: 0.10  # Fundamentals
    technical: 0.05    # Technical indicators

  strategies:
    enabled:
      - "wechat_sentiment_momentum"
      - "event_driven"
      - "value_momentum_combo"
      - "multi_source_weighted"
```

## 💡 Usage Examples

### Example 1: Process WeChat Export

```python
from agents import WxSourceAgent

# Initialize agent
agent = WxSourceAgent()

# Process WeChat export
results = agent.run(
    wechat_export_path="/path/to/export",
    export_type="auto",  # Auto-detect format
    process_images=True,  # OCR images
    process_links=True,   # Follow article links
)

print(f"Processed {results['processed_messages']} messages")
print(f"Extracted {results['processed_articles']} articles")
```

### Example 2: Generate Stock Picks

```python
from agents import SelectionAgent

# Initialize agent
agent = SelectionAgent()

# Generate picks
results = agent.run(
    mode="both",  # wx_only, wx_plus_external, or both
    lookback_days=7,
    min_confidence=0.7,
)

print(f"Generated {results['total_picks']} stock picks")
print(f"  - WeChat-only: {len(results['wx_only_picks'])}")
print(f"  - WeChat+External: {len(results['wx_plus_external_picks'])}")
```

### Example 3: Execute Trading Strategies

```python
from agents import TradingAgent

# Initialize with capital
agent = TradingAgent(initial_capital=100000)

# Execute pending strategies
results = agent.run(mode="execute")

print(f"Executed {results['executed']} trades")
print(f"Portfolio value: ${agent.get_portfolio_value():,.2f}")
```

## 📊 Dashboard

### Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/dashboard/overview` | Portfolio overview and key metrics |
| `GET /api/dashboard/wechat` | WeChat sentiment and activity |
| `GET /api/dashboard/external` | External sources feed |
| `GET /api/dashboard/picks` | Stock picks table |
| `GET /api/dashboard/fundamentals/{ticker}` | Fundamental data for ticker |
| `GET /api/dashboard/strategies` | Strategy recommendations |
| `GET /api/dashboard/performance` | Portfolio performance & equity curve |
| `GET /api/chat/context/{ticker}` | Complete context for chat agent |

### Dashboard UI

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## 🎯 Key Features

### 1. WeChat Priority (Mandatory)
- WeChat signals **ALWAYS have ≥60% weight**
- Two operating modes:
  - **WeChat-Only**: 100% WeChat signals
  - **WeChat + External**: ≥60% WeChat, ≤40% external

### 2. Evidence-Based Picks
Every stock pick includes:
- ✅ Ticker symbol
- ✅ Action (BUY/SELL)
- ✅ Price target
- ✅ Trigger event
- ✅ ≥3 reasons
- ✅ WeChat evidence (messages/articles)
- ✅ External evidence (if applicable)
- ✅ Confidence score

### 3. Comprehensive Fundamentals
For each picked stock:
- Company overview & business model
- Financial metrics (revenue, margins, ROE, ROA)
- Valuation ratios (PE, PB, PS, PEG, EV/EBITDA)
- DCF fair value calculation
- Latest filings (10-K, 10-Q, 8-K)
- Analyst ratings & price targets
- Recent news & events

### 4. Multi-Strategy Framework
Four primary strategies:
1. **WeChat Sentiment Momentum** (40% allocation)
2. **Event-Driven** (30% allocation)
3. **Value-Momentum Combo** (20% allocation)
4. **Multi-Source Weighted** (10% allocation)

### 5. Risk Management
- Position sizing based on confidence
- Stop-loss and take-profit levels
- Portfolio-level risk constraints
- Maximum position size limits
- Sector concentration limits

### 6. Paper Trading Simulation
- Realistic order execution (slippage, commissions)
- Position monitoring with automatic stops
- Real-time P&L tracking
- Equity curve visualization
- Performance metrics (Sharpe, max drawdown, win rate)

### 7. Memory & Context
- Vector embeddings for semantic search
- Conversational memory
- Context routing
- Query rewriting
- Ticker-specific context aggregation

## 📄 License

[MIT License](LICENSE)

## 🙏 Acknowledgments

- **Claude Sonnet 4.5** by Anthropic for LLM capabilities
- **Supabase** for database infrastructure
- **OpenBB** for financial data
- **Tushare/AKShare** for Chinese market data
- WeChat export tools: WeChatMsg, WechatExporter

---

**⚠️ DISCLAIMER**: This is a paper trading system for educational and research purposes only. Not financial advice. Always do your own research before making investment decisions. Past performance does not guarantee future results.
