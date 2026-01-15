"""
Signal Service
Business logic for signal processing, caching, and filtering
"""

import time
import os
from datetime import datetime, timezone
from typing import Dict, Optional
import logging

from backend.services.quantix_client import fetch_quantix_signal

logger = logging.getLogger(__name__)

# Configuration
CONF_THRESHOLD = float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.85"))
TTL = int(os.getenv("SIGNAL_TTL_SECONDS", "900"))  # 15 minutes

# In-memory cache
_cache = {
    "data": None,
    "timestamp": 0
}

def get_latest_signal(asset: str) -> Dict:
    """
    Get latest high-confidence signal with caching
    """
    now = time.time()
    
    # 1️⃣ Check TTL Cache
    if _cache["data"] and now - _cache["timestamp"] < TTL:
        logger.info(f"Returning cached signal for {asset}")
        return {
            **_cache["data"],
            "source": "cache",
            "cache_age": int(now - _cache["timestamp"])
        }
    
    # 2️⃣ Call Quantix AI Core
    try:
        signal = fetch_quantix_signal({
            "asset": asset,
            "timeframe": "M15",
            "session": "London-NewYork",
            "mode": "intraday"
        })
    except Exception as e:
        logger.error(f"Failed to fetch from Quantix: {e}")
        # Return cached data if available (even if expired)
        if _cache["data"]:
            logger.warning("Returning stale cache due to API failure")
            return {
                **_cache["data"],
                "source": "cache_stale",
                "error": "API unavailable"
            }
        # Return mock data as fallback
        return get_mock_signal(asset)
    
    # 3️⃣ Confidence Gate
    confidence = signal.get("confidence", 0)
    if confidence < CONF_THRESHOLD:
        logger.info(f"Signal confidence {confidence} below threshold {CONF_THRESHOLD}")
        return {
            "status": "no_signal",
            "confidence": round(confidence * 100),
            "threshold": round(CONF_THRESHOLD * 100),
            "message": f"AI confidence {round(confidence * 100)}% is below minimum threshold {round(CONF_THRESHOLD * 100)}%"
        }
    
    # 4️⃣ Normalize Output
    result = normalize_signal(signal)
    
    # 5️⃣ Update Cache
    _cache["data"] = result
    _cache["timestamp"] = now
    
    logger.info(f"New signal cached for {asset}")
    return result

def normalize_signal(signal: Dict) -> Dict:
    """
    Normalize Quantix signal to standard rich format with confidence tiers
    """
    asset = signal.get("asset", "EUR/USD")
    direction = signal.get("direction", "BUY").upper()
    entry = signal.get("entry", [0, 0])
    tp = signal.get("tp", 0)
    sl = signal.get("sl", 0)
    conf_value = round(signal.get("confidence", 0) * 100)
    
    # Confidence Tier Mapping
    if conf_value >= 95:
        tier = "HIGH"
        tier_label = f"STRONG {direction}"
        tier_color = "green"
        risk_note = "High-confidence AI signal. Suitable for execution."
        telegram_eligible = True
    elif conf_value >= 85:
        tier = "MEDIUM"
        tier_label = "EXPERIMENTAL"
        tier_color = "yellow"
        risk_note = "⚠️ Experimental signal. Lower confidence. For observation or confirmation only."
        telegram_eligible = False
    else:
        tier = "LOW"
        tier_label = "NO SIGNAL"
        tier_color = "gray"
        risk_note = "No actionable signal at the moment."
        telegram_eligible = False

    # Ensure entry is a list
    entry_list = entry if isinstance(entry, list) else [entry, entry]
    entry_mid = (entry_list[0] + entry_list[1]) / 2
    
    # Calculations
    target_pips = abs(int((tp - entry_mid) * 10000))
    risk = abs(entry_mid - sl)
    reward = abs(tp - entry_mid)
    rr_ratio = f"1 : {round(reward / risk, 2)}" if risk > 0 else "N/A"
    
    return {
        "asset": asset,
        "direction": direction,
        "direction_icon": "🟢" if direction == "BUY" else "🔴",
        "timeframe": signal.get("timeframe", "M15"),
        "session": "London → New York Overlap",
        "confidence": conf_value,
        "confidence_tier": tier,
        "tier_label": tier_label,
        "tier_color": tier_color,
        "risk_note": risk_note,
        "telegram_eligible": telegram_eligible,
        "price_levels": {
            "entry_zone": [str(round(e, 5)) for e in entry_list],
            "take_profit": str(round(tp, 5)),
            "stop_loss": str(round(sl, 5))
        },
        "trade_details": {
            "target_pips": target_pips,
            "risk_reward": rr_ratio,
            "suggested_risk": "0.5% – 1%"
        },
        "trade_type": "Intraday",
        "posted_at_utc": datetime.now(timezone.utc).isoformat(),
        "expiry_rules": {
            "session_only": True,
            "expires_at": "NY_CLOSE",
            "invalidate_if_missed_entry": True
        },
        "disclaimer": "Not financial advice. Trade responsibly.",
        "source": "quantix",
        "reasoning": signal.get("reasoning", {})
    }

def get_mock_signal(asset: str) -> Dict:
    """
    Return mock signal as fallback when Quantix API is unavailable
    """
    logger.warning(f"Returning mock signal for {asset}")
    
    now = datetime.now(timezone.utc)
    
    return {
        "asset": asset,
        "direction": "BUY",
        "direction_icon": "🟢",
        "timeframe": "M15",
        "session": "London → New York Overlap",
        "confidence": 96,
        "confidence_tier": "HIGH",
        "tier_label": "STRONG BUY",
        "tier_color": "green",
        "risk_note": "High-confidence AI signal. Suitable for execution.",
        "telegram_eligible": True,
        "price_levels": {
            "entry_zone": ["1.16710", "1.16750"],
            "take_profit": "1.17080",
            "stop_loss": "1.16480"
        },
        "trade_details": {
            "target_pips": 35,
            "risk_reward": "1 : 1.40",
            "suggested_risk": "0.5% – 1%"
        },
        "trade_type": "Intraday",
        "posted_at_utc": now.isoformat(),
        "expiry_rules": {
            "session_only": True,
            "expires_at": "NY_CLOSE",
            "invalidate_if_missed_entry": True
        },
        "disclaimer": "Not financial advice. Trade responsibly.",
        "source": "mock",
        "reasoning": {
            "note": "This is a mock signal. Quantix AI Core is unavailable."
        }
    }

def clear_cache():
    """Clear the signal cache"""
    global _cache
    _cache = {"data": None, "timestamp": 0}
    logger.info("Cache cleared")
