from datetime import datetime, timezone, timedelta
import math

def calc_ema(values, period):
    if not values or len(values) < period:
        return values[-1] if values else 0
    k = 2 / (period + 1)
    ema = sum(values[:period]) / period # Simple Start
    for v in values[period:]:
        ema = v * k + ema * (1 - k)
    return ema

def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(0, diff))
        losses.append(max(0, -diff))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_atr(candles, period=14):
    if len(candles) < period:
        return 0.0010 # Default for EUR/USD
    tr_list = []
    for i in range(1, len(candles)):
        h = float(candles[i]['high'])
        l = float(candles[i]['low'])
        pc = float(candles[i-1]['close'])
        tr = max(h - l, abs(h - pc), abs(l - pc))
        tr_list.append(tr)
    return sum(tr_list[-period:]) / period

def generate_signal(candles, timeframe="M15"):
    closes = [float(c["close"]) for c in candles]
    current_price = closes[-1]
    
    # 1. Calculate Indicators
    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50)
    rsi = calc_rsi(closes)
    atr = calc_atr(candles)
    
    # 2. Determine Direction
    # Rule: Primary Trend via EMA, Secondary via RSI/Price
    is_up = ema20 > ema50
    direction = "BUY" if is_up else "SELL"
    
    # 3. Confidence Scoring (Points System)
    score = 0
    # EMA Trend (30 pts)
    if (direction == "BUY" and ema20 > ema50) or (direction == "SELL" and ema20 < ema50):
        score += 30
        
    # RSI Region (25 pts)
    if (direction == "BUY" and rsi > 55) or (direction == "SELL" and rsi < 45):
        score += 25
    elif 45 <= rsi <= 55:
        score += 10 # Neutral momentum
        
    # ATR Volatility (15 pts)
    # Average ATR for EUR/USD M15 is around 5-10 pips
    if atr > 0.0005: 
        score += 15
        
    # Candle Confirm (15 pts)
    if (direction == "BUY" and current_price > ema20) or (direction == "SELL" and current_price < ema20):
        score += 15
        
    # Session Score (15 pts) - Simulating London/NY logic
    hour = datetime.now(timezone.utc).hour
    if 8 <= hour <= 18: # Common overlap/active hours
        score += 15
    else:
        score += 5

    confidence = min(score, 95)
    conf_level = "HIGH" if confidence >= 90 else "MEDIUM" if confidence >= 75 else "LOW"

    # 4. Entry / TP / SL (ATR-based)
    # TP: 2.0 * ATR, SL: 1.2 * ATR
    entry = round(current_price, 5)
    dist_tp = atr * 2.0
    dist_sl = atr * 1.2
    
    # Ensure minimum distances for realistic demo
    dist_tp = max(dist_tp, 0.0030)
    dist_sl = max(dist_sl, 0.0020)

    tp = round(entry + dist_tp if direction == "BUY" else entry - dist_tp, 5)
    sl = round(entry - dist_sl if direction == "BUY" else entry + dist_sl, 5)

    # 5. Timing
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=30) # M15 * 2

    return {
        "valid": True,
        "symbol": "EUR/USD",
        "asset": "EUR/USD", # Compatibility
        "timeframe": timeframe,
        "direction": direction,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "confidence": confidence,
        "confidence_level": conf_level,
        "strategy": "EMA20-50 + RSI + ATR",
        "session": "London-NewYork" if 8 <= hour <= 18 else "Asian-Sidney",
        "generated_at": now.isoformat(),
        "expires_at": expiry.isoformat(),
        "source": "rule-engine",
        "market": "real"
    }
