-- Recommended Indexes for Quantix History Tab Performance
-- Target Table: fx_signals

-- 1. Index on timestamp for general sorting (Newest/Oldest First)
CREATE INDEX IF NOT EXISTS idx_fx_signals_generated_at_desc 
ON fx_signals(generated_at DESC);

-- 2. Composite index for Asset + Timeframe filtering
CREATE INDEX IF NOT EXISTS idx_fx_signals_asset_tf_generated 
ON fx_signals(asset, timeframe, generated_at DESC);

-- 3. Composite index for Outcome (State) filtering
CREATE INDEX IF NOT EXISTS idx_fx_signals_state_generated 
ON fx_signals(state, generated_at DESC);

-- 4. Index for Date Range filtering (Already partially covered by idx 1, but specific for pagination)
-- (PostgreSQL indexes are already efficient for range scans on single columns)

-- Note: These indexes ensure that when filtering by Asset or Outcome, 
-- the database doesn't perform a full table scan, keeping the History tab fast
-- even with thousands of signals.
