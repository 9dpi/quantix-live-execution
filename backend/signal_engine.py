from datetime import datetime, timezone, timedelta

def calc_ema(values, period):
    if not values:
        return 0
    k = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]:
        ema = v * k + ema * (1 - k)
    return ema

def generate_signal(candles, timeframe="M15"):
    closes = [float(c["close"]) for c in candles]

    if len(closes) < 50:
        # Fallback if not enough data
        ema20 = calc_ema(closes[-20:], 20) if len(closes) >= 20 else closes[-1]
        ema50 = ema20
    else:
        ema20 = calc_ema(closes[-20:], 20)
        ema50 = calc_ema(closes[-50:], 50)

    direction = "BUY" if ema20 > ema50 else "SELL"

    # trend_score: based on EMA distance
    trend_score = 40 if abs(ema20 - ema50) / ema50 > 0.0005 else 25
    
    # momentum_score: price change over last 5 candles
    momentum_score = min(40, abs(closes[-1] - closes[-5]) * 10000) if len(closes) >= 5 else 20
    
    # session_score: placeholder for session logic
    session_score = 15  

    confidence = int(trend_score + momentum_score + session_score)
    confidence = min(confidence, 95)

    price = closes[-1]
    pip = 0.0001

    entry = [round(price - pip*2, 5), round(price + pip*2, 5)]
    tp = round(price + pip*35 if direction == "BUY" else price - pip*35, 5)
    sl = round(price - pip*25 if direction == "BUY" else price + pip*25, 5)

    expiry = datetime.now(timezone.utc) + timedelta(minutes=20)

    # Added session and source to match simplified FE needs
    # Note: sources in FE were hardcoded or based on data.source
    return {
        "status": "ok",
        "source": "twelvedata",
        "asset": "EUR/USD",
        "direction": direction,
        "confidence": confidence,
        "confidence_note": "EMA trend + momentum + session",
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "timeframe": timeframe,
        "session": "London/NY Overlap", # Logic placeholder
        "expires_at": expiry.isoformat()
    }
