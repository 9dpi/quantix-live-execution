from market import get_price
from datetime import datetime, timezone

def get_latest_signal():
    price = get_price()

    return {
        "asset": "EUR/USD",
        "direction": "BUY",
        "entry": round(price, 5),
        "tp": round(price + 0.0020, 5),
        "sl": round(price - 0.0015, 5),
        "confidence": 60,
        "strategy": "Trend Follow v1",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
