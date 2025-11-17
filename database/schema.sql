-- Multi-Agent Trading System Database Schema
-- Supabase PostgreSQL with pgvector extension

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Agent 1: WeChat Source Tables
-- ============================================

-- WeChat raw messages
CREATE TABLE wx_raw_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id VARCHAR(255) NOT NULL,
    chat_name VARCHAR(500),
    message_id VARCHAR(255) UNIQUE,
    sender VARCHAR(255),
    sender_id VARCHAR(255),
    message_type VARCHAR(50), -- text, image, link, file, video
    content TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    attachments JSONB,
    links TEXT[],
    mentions TEXT[],
    is_group BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_wx_timestamp (timestamp DESC),
    INDEX idx_wx_chat (chat_id, timestamp DESC),
    INDEX idx_wx_sender (sender_id)
);

-- WeChat public account articles
CREATE TABLE wx_mp_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id VARCHAR(255) UNIQUE,
    mp_name VARCHAR(500),
    mp_id VARCHAR(255),
    title TEXT NOT NULL,
    author VARCHAR(255),
    content TEXT,
    summary TEXT,
    publish_time TIMESTAMP WITH TIME ZONE,
    url TEXT,
    cover_image TEXT,
    read_count INTEGER,
    like_count INTEGER,
    tags TEXT[],
    extracted_tickers TEXT[],
    sentiment_score FLOAT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_mp_publish (publish_time DESC),
    INDEX idx_mp_name (mp_name)
);

-- ============================================
-- Agent 2: External Source Tables
-- ============================================

CREATE TABLE external_raw_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(100) NOT NULL, -- twitter, reddit, github, producthunt, news, edgar, etc
    source_id VARCHAR(500) UNIQUE,
    item_type VARCHAR(50), -- tweet, post, article, filing, etc
    author VARCHAR(500),
    author_id VARCHAR(255),
    title TEXT,
    content TEXT,
    url TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    engagement_metrics JSONB, -- likes, shares, comments, etc
    extracted_tickers TEXT[],
    sentiment_score FLOAT,
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_external_source (source, published_at DESC),
    INDEX idx_external_published (published_at DESC)
);

-- ============================================
-- Agent 3: Selection Agent Tables
-- ============================================

-- WeChat-only stock picks
CREATE TABLE stock_picks_wx_only (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(500),
    action VARCHAR(10), -- BUY, SELL, HOLD
    recommended_price DECIMAL(10, 2),
    price_range_low DECIMAL(10, 2),
    price_range_high DECIMAL(10, 2),
    trigger_event TEXT,
    trigger_time TIMESTAMP WITH TIME ZONE,
    confidence_score FLOAT NOT NULL,
    reasons TEXT[],
    wx_evidence JSONB NOT NULL, -- WeChat messages/articles that support this pick
    wx_mention_count INTEGER,
    wx_sentiment_score FLOAT,
    wx_signal_strength FLOAT,
    selection_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active', -- active, executed, expired, cancelled
    metadata JSONB,
    INDEX idx_picks_wx_ticker (ticker, selection_date DESC),
    INDEX idx_picks_wx_status (status),
    INDEX idx_picks_wx_confidence (confidence_score DESC)
);

-- WeChat + External stock picks
CREATE TABLE stock_picks_wx_plus_external (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(500),
    action VARCHAR(10), -- BUY, SELL, HOLD
    recommended_price DECIMAL(10, 2),
    price_range_low DECIMAL(10, 2),
    price_range_high DECIMAL(10, 2),
    trigger_event TEXT,
    trigger_time TIMESTAMP WITH TIME ZONE,
    confidence_score FLOAT NOT NULL,
    reasons TEXT[],

    -- WeChat signals (MUST be >= 0.6 weight)
    wx_evidence JSONB NOT NULL,
    wx_weight FLOAT NOT NULL CHECK (wx_weight >= 0.6),
    wx_mention_count INTEGER,
    wx_sentiment_score FLOAT,

    -- External signals (max 0.4 weight)
    external_evidence JSONB,
    external_weight FLOAT CHECK (external_weight <= 0.4),
    external_source_count INTEGER,
    external_sentiment_score FLOAT,

    -- Combined metrics
    combined_signal_strength FLOAT,
    selection_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,

    INDEX idx_picks_combined_ticker (ticker, selection_date DESC),
    INDEX idx_picks_combined_status (status),
    INDEX idx_picks_combined_confidence (confidence_score DESC),
    CONSTRAINT weight_sum_check CHECK (wx_weight + external_weight <= 1.0)
);

-- ============================================
-- Agent 4: Fundamental Agent Tables
-- ============================================

CREATE TABLE stock_fundamentals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(500),
    sector VARCHAR(255),
    industry VARCHAR(255),
    gics_sector VARCHAR(255),
    gics_industry VARCHAR(255),

    -- Business overview
    business_summary TEXT,
    business_segments JSONB,
    market_cap BIGINT,

    -- Financial metrics
    revenue DECIMAL(20, 2),
    net_income DECIMAL(20, 2),
    gross_margin FLOAT,
    operating_margin FLOAT,
    net_margin FLOAT,
    roe FLOAT,
    roa FLOAT,

    -- Valuation metrics
    pe_ratio FLOAT,
    pb_ratio FLOAT,
    ps_ratio FLOAT,
    peg_ratio FLOAT,
    ev_ebitda FLOAT,
    dividend_yield FLOAT,

    -- DCF valuation
    dcf_fair_value DECIMAL(10, 2),
    dcf_assumptions JSONB,

    -- Latest filings
    latest_10k_date DATE,
    latest_10q_date DATE,
    latest_earnings_date DATE,
    earnings_transcript TEXT,

    -- Analyst notes
    analyst_ratings JSONB,
    price_targets JSONB,

    -- News & events
    recent_news JSONB,
    recent_events JSONB,

    data_date DATE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,

    INDEX idx_fundamentals_ticker (ticker, data_date DESC),
    INDEX idx_fundamentals_sector (sector),
    UNIQUE (ticker, data_date)
);

-- ============================================
-- Agent 5: Strategy Agent Tables
-- ============================================

CREATE TABLE strategy_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_name VARCHAR(255) NOT NULL,
    strategy_type VARCHAR(100), -- sentiment_momentum, event_driven, value_momentum, multi_source

    ticker VARCHAR(20) NOT NULL,
    action VARCHAR(10), -- BUY, SELL, HOLD
    recommended_shares INTEGER,
    recommended_price DECIMAL(10, 2),
    position_size_pct FLOAT,

    -- Risk management
    stop_loss DECIMAL(10, 2),
    take_profit DECIMAL(10, 2),
    max_loss_pct FLOAT,
    max_gain_pct FLOAT,

    -- Signal sources
    signal_breakdown JSONB, -- weights from each source
    wechat_signal_weight FLOAT,
    external_signal_weight FLOAT,
    fundamental_signal_weight FLOAT,
    technical_signal_weight FLOAT,

    -- Strategy parameters
    strategy_params JSONB,
    risk_score FLOAT,
    confidence_score FLOAT,

    -- Backtesting
    backtest_results JSONB,
    expected_return FLOAT,
    sharpe_ratio FLOAT,
    max_drawdown FLOAT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, executed
    metadata JSONB,

    INDEX idx_strategy_ticker (ticker, created_at DESC),
    INDEX idx_strategy_type (strategy_type),
    INDEX idx_strategy_status (status)
);

-- ============================================
-- Agent 6: Trading Agent Tables
-- ============================================

CREATE TABLE executed_trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_output_id UUID REFERENCES strategy_outputs(id),

    ticker VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL, -- BUY, SELL
    shares INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    commission DECIMAL(10, 2),
    slippage DECIMAL(10, 2),

    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_type VARCHAR(50), -- market, limit, stop

    -- P&L tracking
    entry_price DECIMAL(10, 2),
    exit_price DECIMAL(10, 2),
    realized_pnl DECIMAL(15, 2),
    unrealized_pnl DECIMAL(15, 2),
    pnl_pct FLOAT,

    -- Portfolio impact
    portfolio_value_before DECIMAL(20, 2),
    portfolio_value_after DECIMAL(20, 2),
    cash_balance DECIMAL(20, 2),

    metadata JSONB,

    INDEX idx_trades_ticker (ticker, executed_at DESC),
    INDEX idx_trades_date (executed_at DESC)
);

CREATE TABLE backtest_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_name VARCHAR(255) NOT NULL,
    backtest_name VARCHAR(500),

    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20, 2) NOT NULL,
    final_capital DECIMAL(20, 2) NOT NULL,

    -- Performance metrics
    total_return FLOAT,
    annual_return FLOAT,
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT,
    max_drawdown FLOAT,
    win_rate FLOAT,
    profit_factor FLOAT,

    -- Trading stats
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    avg_win DECIMAL(15, 2),
    avg_loss DECIMAL(15, 2),

    -- Risk metrics
    volatility FLOAT,
    beta FLOAT,
    alpha FLOAT,

    -- Equity curve
    equity_curve JSONB,
    drawdown_curve JSONB,

    -- Trade log
    trades JSONB,

    -- Strategy config
    strategy_config JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,

    INDEX idx_backtest_strategy (strategy_name, created_at DESC),
    INDEX idx_backtest_date (start_date, end_date)
);

-- ============================================
-- System & Monitoring Tables
-- ============================================

CREATE TABLE agent_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL, -- running, idle, error, stopped
    last_run_at TIMESTAMP WITH TIME ZONE,
    last_success_at TIMESTAMP WITH TIME ZONE,
    last_error_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    run_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    avg_runtime_ms INTEGER,
    metrics JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE (agent_name)
);

-- ============================================
-- Vector Embeddings for Semantic Search
-- ============================================

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_table VARCHAR(100) NOT NULL, -- wx_raw_messages, external_raw_items, etc
    source_id UUID NOT NULL,
    content_type VARCHAR(50), -- message, article, post, etc
    text_content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-3-large
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    INDEX idx_embeddings_source (source_table, source_id)
);

-- Create vector similarity search index
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================
-- Helper Views
-- ============================================

-- View: Latest stock picks across both tables
CREATE VIEW v_latest_stock_picks AS
SELECT
    'wx_only' as pick_type,
    ticker,
    company_name,
    action,
    confidence_score,
    wx_signal_strength as signal_strength,
    selection_date,
    status
FROM stock_picks_wx_only
UNION ALL
SELECT
    'wx_plus_external' as pick_type,
    ticker,
    company_name,
    action,
    confidence_score,
    combined_signal_strength as signal_strength,
    selection_date,
    status
FROM stock_picks_wx_plus_external
ORDER BY selection_date DESC;

-- View: Portfolio performance summary
CREATE VIEW v_portfolio_summary AS
SELECT
    DATE(executed_at) as trade_date,
    COUNT(*) as trade_count,
    SUM(CASE WHEN action = 'BUY' THEN total_value ELSE 0 END) as total_bought,
    SUM(CASE WHEN action = 'SELL' THEN total_value ELSE 0 END) as total_sold,
    SUM(realized_pnl) as daily_pnl,
    AVG(portfolio_value_after) as avg_portfolio_value
FROM executed_trades
GROUP BY DATE(executed_at)
ORDER BY trade_date DESC;

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================

-- Enable RLS on all tables (optional, configure based on your needs)
-- ALTER TABLE wx_raw_messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE wx_mp_articles ENABLE ROW LEVEL SECURITY;
-- ... add for other tables as needed

-- ============================================
-- Functions & Triggers
-- ============================================

-- Function to update agent status
CREATE OR REPLACE FUNCTION update_agent_status()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for agent_status updates
CREATE TRIGGER trigger_update_agent_status
    BEFORE UPDATE ON agent_status
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_status();

-- Function for semantic search
CREATE OR REPLACE FUNCTION semantic_search(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_table text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    source_table varchar(100),
    source_id uuid,
    text_content text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.source_table,
        e.source_id,
        e.text_content,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM embeddings e
    WHERE (filter_table IS NULL OR e.source_table = filter_table)
        AND 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
