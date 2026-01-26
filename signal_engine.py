import os
import random
from datetime import datetime, timezone
from external_client import get_price

# Import data feed monitor for health tracking
try:
    from data_feed_monitor import DataFeedMonitor
    MONITOR_AVAILABLE = True
except ImportError:
    MONITOR_AVAILABLE = False

LIVE_MODE = os.getenv("LIVE_MODE", "false").lower() == "true"
AI_CORE_API = "https://quantixaicore-production.up.railway.app/api/v1/signals/active"

def is_market_open():
    """Forex market hours: Open Sunday 22:00 UTC to Friday 22:00 UTC"""
    now_utc = datetime.now(timezone.utc)
    weekday = now_utc.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
    hour = now_utc.hour

    if weekday == 5: # Saturday
        return False
    if weekday == 4 and hour >= 22: # Friday late night
        return False
    if weekday == 6 and hour < 22: # Sunday before open
        return False
    
    return True

def consume_ai_core_signal():
    """CONSUMPTION ONLY [T3]: Fetches signal from Immutable Record [T1]"""
    if MONITOR_AVAILABLE:
        try:
            DataFeedMonitor.run_health_check()
        except Exception as e:
            print(f"⚠️ Health check failed: {e}")

    try:
        response = requests.get(AI_CORE_API, timeout=10)
        if response.ok:
            signals = response.json()
            if signals:
                # Get the most recent active signal
                latest = signals[0]
                return {
                    "asset": latest["asset"],
                    "direction": latest["direction"],
                    "strength": "(HIGH)" if latest["ai_confidence"] > 0.8 else "(MID)",
                    "entry": float(latest["entry_low"]),
                    "tp": float(latest["tp"]),
                    "sl": float(latest["sl"]),
                    "confidence": int(latest["ai_confidence"] * 100),
                    "strategy": "Quantix Core [T1] Consumer",
                    "validity": 90,
                    "validity_passed": 0,
                    "volatility": "Verified via Core",
                    "timestamp": latest["generated_at"]
                }
        return None
    except Exception as e:
        print(f"❌ Failed to consume AI Core signal: {e}")
        return None

def get_latest_signal_safe():
    """Execution Layer Entry [T3]"""
    return consume_ai_core_signal()
