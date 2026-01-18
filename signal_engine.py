from market import get_price
from datetime import datetime, timezone
import random

def generate_signal():
    price = get_price()
    confidence = random.randint(55, 95)
    strength = "(HIGH)" if confidence > 75 else "(MID)" if confidence > 60 else "(LOW)"

    return {
        "asset": "EUR/USD",
        "direction": "BUY",
        "strength": strength,
        "entry": round(price, 5),
        "tp": round(price + 0.0020, 5),
        "sl": round(price - 0.0015, 5),
        "confidence": confidence,
        "strategy": "Trend Follow (Stabilizer)",
        "validity": 90,
        "validity_passed": random.randint(30, 85),
        "volatility": "0.12% (Stabilized)",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def generate_stabilizer_signal():
    """Fallback signal when market API or logic fails"""
    return {
        "asset": "EUR/USD",
        "direction": "SIDEWAYS",
        "strength": "(WAIT)",
        "entry": 0.0,
        "tp": 0.0,
        "sl": 0.0,
        "confidence": 0,
        "strategy": "Stabilizer Mode",
        "validity": 90,
        "validity_passed": 0,
        "volatility": "N/A",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def get_latest_signal_safe():
    try:
        return generate_signal()
    except Exception as e:
        print("⚠️ SIGNAL ENGINE ERROR:", e)
        return generate_stabilizer_signal()
