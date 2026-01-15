"""
Signal Service
Business logic for signal processing, caching, and filtering
"""

import time
import os
from datetime import datetime, timezone
from typing import Dict, Optional
import logging

from services.quantix_client import fetch_quantix_signal

logger = logging.getLogger(__name__)

# Configuration
CONF_THRESHOLD = float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.95"))
TTL = int(os.getenv("SIGNAL_TTL_SECONDS", "900"))  # 15 minutes

# In-memory cache
_cache = {
    "data": None,
    "timestamp": 0
}

def get_latest_signal(asset: str) -> Dict:
    """
    Get latest high-confidence signal with caching
    
    Args:
        asset: Trading asset (e.g., "EUR/USD")
        
    Returns:
        Dict: Signal data or no_signal status
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
    Normalize Quantix signal to standard format
    
    Args:
        signal: Raw signal from Quantix AI Core
        
    Returns:
        Dict: Normalized signal data
    """
    entry = signal.get("entry", [0, 0])
    tp = signal.get("tp", 0)
    sl = signal.get("sl", 0)
    
    # Calculate target pips
    if isinstance(entry, list) and len(entry) == 2:
        entry_mid = (entry[0] + entry[1]) / 2
    else:
        entry_mid = entry
    
    target_pips = abs(int((tp - entry_mid) * 10000))
    
    # Calculate risk-reward
    risk = abs(entry_mid - sl)
    reward = abs(tp - entry_mid)
    rr_ratio = f"1 : {round(reward / risk, 2)}" if risk > 0 else "N/A"
    
    return {
        "asset": signal.get("asset", "EUR/USD"),
        "trade": signal.get("direction", "BUY"),
        "entry": entry if isinstance(entry, list) else [entry, entry],
        "tp": tp,
        "sl": sl,
        "confidence": round(signal.get("confidence", 0) * 100),
        "target_pips": target_pips,
        "risk_reward": rr_ratio,
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "expires_in": TTL,
        "source": "quantix",
        "reasoning": signal.get("reasoning", {})
    }

def get_mock_signal(asset: str) -> Dict:
    """
    Return mock signal as fallback when Quantix API is unavailable
    
    Args:
        asset: Trading asset
        
    Returns:
        Dict: Mock signal data
    """
    logger.warning(f"Returning mock signal for {asset}")
    
    return {
        "asset": asset,
        "trade": "BUY",
        "entry": [1.16710, 1.16750],
        "tp": 1.17080,
        "sl": 1.16480,
        "confidence": 96,
        "target_pips": 35,
        "risk_reward": "1 : 1.40",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "expires_in": TTL,
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
