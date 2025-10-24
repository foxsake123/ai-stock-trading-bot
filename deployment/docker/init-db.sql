-- AI Trading Bot - PostgreSQL Initialization Script
-- Last Updated: 2025-10-23
-- Runs automatically when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA trading TO trader;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO trader;

-- Set search path
ALTER DATABASE trading_bot SET search_path TO trading,public;

-- ============================================================================
-- TRADING SCHEMA TABLES
-- ============================================================================

-- Trades table
CREATE TABLE IF NOT EXISTS trading.trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('BUY', 'SELL', 'SHORT', 'COVER')),
    strategy VARCHAR(50) NOT NULL,
    shares INTEGER NOT NULL,
    entry_price NUMERIC(10, 2) NOT NULL,
    exit_price NUMERIC(10, 2),
    stop_loss NUMERIC(10, 2),
    take_profit NUMERIC(10, 2),
    entry_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exit_date TIMESTAMP,
    pnl NUMERIC(12, 2),
    pnl_pct NUMERIC(6, 4),
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'CANCELLED')),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_ticker ON trading.trades(ticker);
CREATE INDEX idx_trades_strategy ON trading.trades(strategy);
CREATE INDEX idx_trades_status ON trading.trades(status);
CREATE INDEX idx_trades_entry_date ON trading.trades(entry_date);

-- Positions table
CREATE TABLE IF NOT EXISTS trading.positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL UNIQUE,
    strategy VARCHAR(50) NOT NULL,
    shares INTEGER NOT NULL,
    avg_entry_price NUMERIC(10, 2) NOT NULL,
    current_price NUMERIC(10, 2),
    market_value NUMERIC(12, 2),
    unrealized_pnl NUMERIC(12, 2),
    unrealized_pnl_pct NUMERIC(6, 4),
    stop_loss NUMERIC(10, 2),
    take_profit NUMERIC(10, 2),
    opened_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_ticker ON trading.positions(ticker);
CREATE INDEX idx_positions_strategy ON trading.positions(strategy);

-- Agent recommendations table
CREATE TABLE IF NOT EXISTS trading.agent_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    agent_name VARCHAR(50) NOT NULL,
    action VARCHAR(10) NOT NULL,
    confidence NUMERIC(4, 3) NOT NULL,
    reasoning TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_recs_ticker ON trading.agent_recommendations(ticker);
CREATE INDEX idx_agent_recs_agent ON trading.agent_recommendations(agent_name);
CREATE INDEX idx_agent_recs_date ON trading.agent_recommendations(date);

-- ============================================================================
-- ANALYTICS SCHEMA TABLES
-- ============================================================================

-- Performance metrics table
CREATE TABLE IF NOT EXISTS analytics.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL UNIQUE,
    strategy VARCHAR(50) NOT NULL,
    total_pnl NUMERIC(12, 2),
    total_pnl_pct NUMERIC(6, 4),
    win_rate NUMERIC(5, 4),
    sharpe_ratio NUMERIC(6, 4),
    max_drawdown NUMERIC(6, 4),
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    avg_win NUMERIC(10, 2),
    avg_loss NUMERIC(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_perf_date ON analytics.performance_metrics(date);
CREATE INDEX idx_perf_strategy ON analytics.performance_metrics(strategy);

-- Pipeline execution log
CREATE TABLE IF NOT EXISTS analytics.pipeline_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'PARTIAL')),
    duration_seconds INTEGER,
    phase_results JSONB,
    errors TEXT[],
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_date ON analytics.pipeline_executions(execution_date);
CREATE INDEX idx_pipeline_status ON analytics.pipeline_executions(status);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_trades_updated_at BEFORE UPDATE ON trading.trades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON trading.positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert sample data for testing (optional - remove in production)
-- INSERT INTO trading.trades (ticker, action, strategy, shares, entry_price, status)
-- VALUES ('AAPL', 'BUY', 'DEE-BOT', 10, 150.00, 'OPEN');

-- ============================================================================
-- NOTES
-- ============================================================================
-- This script runs only on first container start
-- Subsequent restarts will use the persisted volume
-- To reset: docker-compose down -v (WARNING: deletes all data)
