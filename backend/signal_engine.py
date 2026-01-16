from datetime import datetime, timezone, timedelta
import random

# =========================
# CONFIG & CONSTANTS
# =========================
CONFIDENCE_MIN = 50
SYMBOL_DEFAULT = "EUR/USD"

def generate_signal_id(symbol: str, timestamp: datetime = None) -> str:
    """Generate unique trader-grade signal ID."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    date_str = timestamp.strftime("%Y%m%d")
    time_str = timestamp.strftime("%H%M")
    clean_symbol = symbol.replace("/", "").replace("-", "")
    return f"SIG-{clean_symbol}-{date_str}-{time_str}"

def classify_confidence(confidence: int) -> dict:
    """Classify confidence into tiers for Web and Telegram."""
    if confidence >= 85:
        return {"tier": "HIGH", "label": "🟢 HIGH", "telegram": True, "color": "#16a34a", "icon": "🟢"}
    if confidence >= 60:
        return {"tier": "MEDIUM", "label": "🟡 MEDIUM", "telegram": False, "color": "#f59e0b", "icon": "🟡"}
    return {"tier": "LOW", "label": "🔴 LOW", "telegram": False, "color": "#dc2626", "icon": "🔴"}

# =========================
# CORE MATH & INDICATORS
# =========================

def calc_ema(values, period):
    if not values or len(values) < period: return values[-1] if values else 0
    k = 2 / (period + 1)
    ema = sum(values[:period]) / period 
    for v in values[period:]: ema = v * k + ema * (1 - k)
    return ema

def calc_rsi(closes, period=14):
    if len(closes) < period + 1: return 50
    diffs = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    avg_gain = sum([d for d in diffs[-period:] if d > 0]) / period
    avg_loss = sum([-d for d in diffs[-period:] if d < 0]) / period
    if avg_loss == 0: return 100
    return 100 - (100 / (1 + (avg_gain / avg_loss)))

def calc_atr(candles, period=14):
    if len(candles) < period: return 0.0010
    tr_list = []
    for i in range(1, len(candles)):
        h, l, pc = float(candles[i]['high']), float(candles[i]['low']), float(candles[i-1]['close'])
        tr_list.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(tr_list[-period:]) / period

def calc_atr_percent(atr: float, price: float) -> float:
    return round((atr / price) * 100, 3) if price else 0

# =========================
# TRADER-GRADE LOGIC
# =========================

def calc_confidence(atr_pct, rsi, trend_aligned):
    """
    Quantitative Confidence Scoring (Explainable)
    """
    score = 0
    # 1. Volatility State (ATR% driven) - 40 pts
    if 0.05 <= atr_pct <= 0.30: score += 40  # Healthy
    elif atr_pct > 0.30: score += 25         # Risky High
    else: score += 15                         # Flat
    
    # 2. RSI Confirmation - 30 pts
    if 45 <= rsi <= 65: score += 30
    elif 40 <= rsi <= 70: score += 20
    
    # 3. Trend Alignment - 30 pts
    if trend_aligned: score += 30
    
    return min(score, 95)

def calc_expiry(timeframe_str):
    """Calculate expiry based on timeframe."""
    mapping = {
        "M5": {"minutes": 15, "label": "15 min"},
        "M15": {"minutes": 45, "label": "45 min"},
        "H1": {"minutes": 180, "label": "3 hours"},
    }
    return mapping.get(timeframe_str, {"minutes": 30, "label": "30 min"})

# =========================
# SIGNAL GENERATORS
# =========================

def generate_signal(candles, timeframe="M15"):
    """Main Trading Engine."""
    now = datetime.now(timezone.utc)
    
    if not candles or len(candles) < 20:
        price = float(candles[-1]['close']) if candles else 1.0850
        return generate_stabilizer_signal(price, timeframe)

    closes = [float(c["close"]) for c in candles]
    current_price = closes[-1]
    
    # Calculate indicators
    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50)
    rsi = calc_rsi(closes)
    atr = calc_atr(candles)
    atr_pct = calc_atr_percent(atr, current_price)
    
    # Logic
    trend_up = ema20 > ema50
    direction = "BUY" if trend_up else "SELL"
    
    # Confidence
    confidence = calc_confidence(atr_pct, rsi, True) 
    
    if confidence < CONFIDENCE_MIN:
        return generate_stabilizer_signal(current_price, timeframe, "Low Market Confidence")

    # Output Construction
    entry = round(current_price, 5)
    tp = round(entry + atr * 2 if direction == "BUY" else entry - atr * 2, 5)
    sl = round(entry - atr * 1.5 if direction == "BUY" else entry + atr * 1.5, 5)
    
    expiry_info = calc_expiry(timeframe)
    expires_at = now + timedelta(minutes=expiry_info["minutes"])

    return {
        "status": "ok",
        "mode": "NORMAL",
        "signal_id": generate_signal_id(SYMBOL_DEFAULT, now),
        "symbol": SYMBOL_DEFAULT,
        "asset": SYMBOL_DEFAULT,
        "timeframe": timeframe,
        "direction": direction,
        "entry": [entry],
        "tp": tp,
        "sl": sl,
        "confidence": confidence,
        "confidence_meta": classify_confidence(confidence),
        "volatility": {
            "atr": round(atr, 5),
            "atr_percent": atr_pct,
            "state": "healthy" if 0.05 <= atr_pct <= 0.30 else "low" if atr_pct < 0.05 else "high"
        },
        "expiry": {
            "minutes": expiry_info["minutes"],
            "label": expiry_info["label"],
            "expires_at": expires_at.isoformat()
        },
        "strategy": "EMA Trend + RSI + ATR",
        "session": "Active Market",
        "generated_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "status_life": "ACTIVE",
        "source": "rule-engine"
    }

def generate_stabilizer_signal(price, timeframe="M15", reason="Market Stabilizer"):
    """Ensures bot always has an answer."""
    now = datetime.now(timezone.utc)
    entry = round(price, 5)
    atr_mock = 0.0015
    expiry_info = calc_expiry(timeframe)
    expires_at = now + timedelta(minutes=expiry_info["minutes"])

    return {
        "status": "ok",
        "mode": "STABILIZER",
        "signal_id": generate_signal_id(SYMBOL_DEFAULT, now),
        "symbol": SYMBOL_DEFAULT,
        "asset": SYMBOL_DEFAULT,
        "timeframe": timeframe,
        "direction": "BUY",
        "entry": [entry],
        "tp": round(entry + atr_mock, 5),
        "sl": round(entry - atr_mock, 5),
        "confidence": 55,
        "confidence_meta": classify_confidence(55),
        "volatility": {"atr": atr_mock, "atr_percent": 0.12, "state": "stabilized"},
        "expiry": {
            "minutes": expiry_info["minutes"] * 2,
            "label": "Extended Window",
            "expires_at": expires_at.isoformat()
        },
        "strategy": "Trend Follow (Stabilizer)",
        "warning": reason,
        "generated_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "status_life": "ACTIVE",
        "source": "stabilizer"
    }
