"""
Rate Limit & Daily Signal Policy - In-memory Cache
Ensures only one 'fresh' signal per asset/timeframe per day (UTC).
"""
from datetime import datetime, timezone
from typing import Dict, Optional

# In-memory storage: { "EUR/USD_M15_2026-01-16": signal_dict }
_last_signal_cache = {}

def get_daily_key(asset: str, timeframe: str) -> str:
    """Generate a unique key for the day."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"{asset}_{timeframe}_{today}"

def get_cached_daily_signal(asset: str, timeframe: str) -> Optional[Dict]:
    """Retrieve today's signal from cache if it exists."""
    key = get_daily_key(asset, timeframe)
    return _last_signal_cache.get(key)

def save_daily_signal(asset: str, timeframe: str, signal: Dict) -> None:
    """Save today's signal to cache."""
    key = get_daily_key(asset, timeframe)
    _last_signal_cache[key] = signal

def is_signal_fresh(signal_data: Dict) -> bool:
    """Check if the signal matches 'fresh' status."""
    return signal_data.get("meta", {}).get("status") == "fresh"

def should_push_telegram(signal: Dict) -> bool:
    """
    Business Logic: Should we push this signal to Telegram?
    Rules:
    - Must be 'fresh' (no replay)
    - Confidence must be >= 60 (Quality Bar)
    """
    is_fresh = signal.get("meta", {}).get("status") == "fresh"
    confidence = signal.get("confidence", 0)
    
    return is_fresh and confidence >= 60
