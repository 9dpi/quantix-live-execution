-- Signal Genius AI - Supabase Database Schema
-- Version: 1.0
-- Created: 2026-01-15

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- Table: signals
-- Purpose: Store all generated trading signals
-- =====================================================
CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Asset Information
    asset VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('BUY', 'SELL')),
    direction_icon VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    session VARCHAR(100) NOT NULL,
    
    -- Price Levels (stored as JSONB for flexibility)
    price_levels JSONB NOT NULL,
    -- Example: {"entry_zone": ["1.16710", "1.16750"], "take_profit": "1.17080", "stop_loss": "1.16480"}
    
    -- Trade Details
    trade_details JSONB NOT NULL,
    -- Example: {"target_pips": 35, "risk_reward": "1 : 1.40", "suggested_risk": "0.5% – 1%"}
    
    trade_type VARCHAR(50) NOT NULL,
    confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    
    -- Timestamps
    posted_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    posted_date DATE GENERATED ALWAYS AS (DATE(posted_at_utc)) STORED,
    expires_at_utc TIMESTAMPTZ,
    
    -- Expiry Rules
    expiry_rules JSONB,
    -- Example: {"session_only": true, "expires_at": "NY_CLOSE", "invalidate_if_missed_entry": true}
    
    -- Status Tracking
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'hit_tp', 'hit_sl', 'cancelled')),
    
    -- Results (filled after signal closes)
    result VARCHAR(20) CHECK (result IN ('win', 'loss', 'breakeven', 'pending', NULL)),
    actual_pips DECIMAL(10, 2),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint: one signal per asset per direction per day
    CONSTRAINT unique_signal_per_day UNIQUE (asset, direction, posted_date)
);

-- Create indexes for performance
CREATE INDEX idx_signals_asset ON signals(asset);
CREATE INDEX idx_signals_posted_at ON signals(posted_at_utc DESC);
CREATE INDEX idx_signals_posted_date ON signals(posted_date);
CREATE INDEX idx_signals_status ON signals(status);
CREATE INDEX idx_signals_confidence ON signals(confidence);

-- =====================================================
-- Table: signal_history
-- Purpose: Archive of all signals for analytics
-- =====================================================
CREATE TABLE IF NOT EXISTS signal_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id UUID REFERENCES signals(id) ON DELETE CASCADE,
    
    -- Snapshot of signal data at time of archival
    signal_data JSONB NOT NULL,
    
    -- Performance metrics
    win_rate DECIMAL(5, 2),
    total_pips DECIMAL(10, 2),
    
    archived_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signal_history_signal_id ON signal_history(signal_id);
CREATE INDEX idx_signal_history_archived_at ON signal_history(archived_at DESC);

-- =====================================================
-- Table: telegram_subscribers
-- Purpose: Track Telegram users/groups receiving signals
-- =====================================================
CREATE TABLE IF NOT EXISTS telegram_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    chat_id BIGINT UNIQUE NOT NULL,
    chat_type VARCHAR(20) CHECK (chat_type IN ('private', 'group', 'supergroup', 'channel')),
    
    -- User/Group info
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    title VARCHAR(200), -- For groups/channels
    
    -- Subscription status
    is_active BOOLEAN DEFAULT true,
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    
    -- Preferences
    preferences JSONB DEFAULT '{}',
    -- Example: {"min_confidence": 95, "assets": ["EUR/USD"], "timeframes": ["M15"]}
    
    -- Stats
    signals_received INTEGER DEFAULT 0,
    last_signal_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_telegram_subscribers_chat_id ON telegram_subscribers(chat_id);
CREATE INDEX idx_telegram_subscribers_active ON telegram_subscribers(is_active);

-- =====================================================
-- Table: signal_deliveries
-- Purpose: Track which signals were sent to which subscribers
-- =====================================================
CREATE TABLE IF NOT EXISTS signal_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    signal_id UUID REFERENCES signals(id) ON DELETE CASCADE,
    subscriber_id UUID REFERENCES telegram_subscribers(id) ON DELETE CASCADE,
    
    delivered_at TIMESTAMPTZ DEFAULT NOW(),
    delivery_status VARCHAR(20) DEFAULT 'sent' CHECK (delivery_status IN ('sent', 'failed', 'pending')),
    error_message TEXT,
    
    -- Engagement tracking
    message_id BIGINT, -- Telegram message ID
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signal_deliveries_signal_id ON signal_deliveries(signal_id);
CREATE INDEX idx_signal_deliveries_subscriber_id ON signal_deliveries(subscriber_id);
CREATE INDEX idx_signal_deliveries_delivered_at ON signal_deliveries(delivered_at DESC);

-- =====================================================
-- Table: analytics
-- Purpose: Store daily/weekly/monthly performance metrics
-- =====================================================
CREATE TABLE IF NOT EXISTS analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Signal metrics
    total_signals INTEGER DEFAULT 0,
    signals_with_result INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    breakevens INTEGER DEFAULT 0,
    
    -- Performance metrics
    win_rate DECIMAL(5, 2),
    total_pips DECIMAL(10, 2),
    avg_confidence DECIMAL(5, 2),
    
    -- Asset breakdown
    asset_breakdown JSONB,
    -- Example: {"EUR/USD": {"signals": 10, "wins": 7, "pips": 150}}
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_analytics_period UNIQUE (period_type, period_start)
);

CREATE INDEX idx_analytics_period ON analytics(period_type, period_start DESC);

-- =====================================================
-- Table: api_logs
-- Purpose: Log API requests for monitoring and debugging
-- =====================================================
CREATE TABLE IF NOT EXISTS api_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    
    -- Request details
    query_params JSONB,
    request_body JSONB,
    
    -- Response details
    status_code INTEGER,
    response_time_ms INTEGER,
    
    -- Client info
    ip_address INET,
    user_agent TEXT,
    
    -- Error tracking
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at DESC);
CREATE INDEX idx_api_logs_status_code ON api_logs(status_code);

-- =====================================================
-- Functions: Auto-update timestamps
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at
CREATE TRIGGER update_signals_updated_at BEFORE UPDATE ON signals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_telegram_subscribers_updated_at BEFORE UPDATE ON telegram_subscribers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Functions: Auto-expire signals
-- =====================================================
CREATE OR REPLACE FUNCTION auto_expire_signals()
RETURNS void AS $$
BEGIN
    UPDATE signals
    SET status = 'expired'
    WHERE status = 'active'
    AND expires_at_utc IS NOT NULL
    AND expires_at_utc < NOW();
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Views: Useful queries
-- =====================================================

-- Active signals view
CREATE OR REPLACE VIEW active_signals AS
SELECT 
    id,
    asset,
    direction,
    direction_icon,
    timeframe,
    session,
    price_levels,
    trade_details,
    confidence,
    posted_at_utc,
    expires_at_utc
FROM signals
WHERE status = 'active'
ORDER BY posted_at_utc DESC;

-- Performance summary view
CREATE OR REPLACE VIEW performance_summary AS
SELECT 
    asset,
    COUNT(*) as total_signals,
    COUNT(CASE WHEN result = 'win' THEN 1 END) as wins,
    COUNT(CASE WHEN result = 'loss' THEN 1 END) as losses,
    ROUND(
        COUNT(CASE WHEN result = 'win' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(CASE WHEN result IS NOT NULL THEN 1 END), 0) * 100, 
        2
    ) as win_rate,
    SUM(actual_pips) as total_pips,
    AVG(confidence) as avg_confidence
FROM signals
WHERE result IS NOT NULL
GROUP BY asset
ORDER BY total_signals DESC;

-- Recent deliveries view
CREATE OR REPLACE VIEW recent_deliveries AS
SELECT 
    sd.id,
    s.asset,
    s.direction,
    s.confidence,
    ts.chat_id,
    ts.username,
    sd.delivered_at,
    sd.delivery_status
FROM signal_deliveries sd
JOIN signals s ON sd.signal_id = s.id
JOIN telegram_subscribers ts ON sd.subscriber_id = ts.id
ORDER BY sd.delivered_at DESC
LIMIT 100;

-- =====================================================
-- Row Level Security (RLS) - Optional
-- =====================================================

-- Enable RLS on tables (uncomment if needed)
-- ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE signal_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE telegram_subscribers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE signal_deliveries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE api_logs ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your auth setup)
-- CREATE POLICY "Public read access for active signals" ON signals
--     FOR SELECT USING (status = 'active');

-- =====================================================
-- Sample Data (for testing)
-- =====================================================

-- Insert a sample signal
INSERT INTO signals (
    asset,
    direction,
    direction_icon,
    timeframe,
    session,
    price_levels,
    trade_details,
    trade_type,
    confidence,
    posted_at_utc,
    expiry_rules
) VALUES (
    'EUR/USD',
    'BUY',
    '🟢',
    'M15',
    'London → New York Overlap',
    '{"entry_zone": ["1.16710", "1.16750"], "take_profit": "1.17080", "stop_loss": "1.16480"}'::jsonb,
    '{"target_pips": 35, "risk_reward": "1 : 1.40", "suggested_risk": "0.5% – 1%"}'::jsonb,
    'Intraday',
    96,
    NOW(),
    '{"session_only": true, "expires_at": "NY_CLOSE", "invalidate_if_missed_entry": true}'::jsonb
);

-- =====================================================
-- Maintenance: Scheduled tasks (run via cron or pg_cron)
-- =====================================================

-- Auto-expire old signals (run every hour)
-- SELECT cron.schedule('auto-expire-signals', '0 * * * *', 'SELECT auto_expire_signals();');

-- Archive old signals (run daily)
-- SELECT cron.schedule('archive-old-signals', '0 2 * * *', $$
--     INSERT INTO signal_history (signal_id, signal_data)
--     SELECT id, row_to_json(signals.*)
--     FROM signals
--     WHERE status IN ('expired', 'hit_tp', 'hit_sl')
--     AND created_at < NOW() - INTERVAL '30 days';
-- $$);

-- =====================================================
-- End of Schema
-- =====================================================

COMMENT ON TABLE signals IS 'Stores all trading signals generated by Signal Genius AI';
COMMENT ON TABLE signal_history IS 'Archive of historical signals for analytics';
COMMENT ON TABLE telegram_subscribers IS 'Telegram users/groups subscribed to signals';
COMMENT ON TABLE signal_deliveries IS 'Tracks signal delivery to subscribers';
COMMENT ON TABLE analytics IS 'Aggregated performance metrics';
COMMENT ON TABLE api_logs IS 'API request logs for monitoring';
