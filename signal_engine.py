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
AI_CORE_API = "https://quantixaicore-production.up.railway.app/api/v1/active"

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
        # 1. NEW: Try Supabase Direct (Preferred)
        # ----------------------------------------
        sb_url = os.getenv("SUPABASE_URL")
        sb_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if sb_url and sb_key:
            try:
                # Fetch latest ACTIVE signal
                url = f"{sb_url}/rest/v1/fx_signals?select=*&status=eq.ACTIVE&order=generated_at.desc&limit=1"
                headers = {
                    "apikey": sb_key, 
                    "Authorization": f"Bearer {sb_key}",
                    "Content-Type": "application/json"
                }
                resp = requests.get(url, headers=headers, timeout=5)
                
                if resp.ok:
                    data = resp.json()
                    if data:
                        latest = data[0]
                        print(f"✅ Extracted signal from Supabase: {latest['id']}")
                        return {
                            "asset": latest.get("asset", "EUR/USD"),
                            "direction": latest.get("direction", "NEUTRAL"),
                            "strength": "(HIGH)" if float(latest.get("ai_confidence", 0)) > 0.8 else "(MID)",
                            "entry": float(latest.get("entry_low", 0)), # Use entry_low as main
                            "tp": float(latest.get("tp", 0)),
                            "sl": float(latest.get("sl", 0)),
                            "confidence": int(float(latest.get("ai_confidence", 0)) * 100),
                            "strategy": latest.get("strategy", "Quantix Core [Hybrid]"),
                            "validity": 90,
                            "validity_passed": 0,
                            "volatility": "Verified",
                            "timestamp": latest.get("generated_at")
                        }
            except Exception as sb_err:
                print(f"⚠️ Supabase fetch failed: {sb_err}")
                
        # 2. OLD: Fallback to REST API (Deprecated)
        # -----------------------------------------
        print(f"🔄 Trying legacy API: {AI_CORE_API}")
        response = requests.get(AI_CORE_API, timeout=10)
        if response.ok:
             # ... existing mapping logic ...
            signals = response.json()
            if signals:
                latest = signals[0]
                return {
                    "asset": latest["asset"],
                    "direction": latest["direction"],
                    "strength": "(HIGH)" if latest["ai_confidence"] > 0.8 else "(MID)",
                    "entry": float(latest.get("entry_low", 0)),
                    "tp": float(latest.get("tp", 0)),
                    "sl": float(latest.get("sl", 0)),
                    "confidence": int(latest["ai_confidence"] * 100),
                    "strategy": "Quantix Core [Legacy]",
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
