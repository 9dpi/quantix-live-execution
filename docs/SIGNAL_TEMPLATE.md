# Signal Template - Signal Genius AI

This document defines the canonical signal format used across all platforms (Web, Telegram, API).

## Signal Schema

```json
{
  "asset": "EUR/USD",
  "direction": "BUY",
  "direction_icon": "🟢",
  "timeframe": "M15",
  "session": "London → New York Overlap",
  
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
  "confidence": 96,
  
  "posted_at_utc": "2026-01-13T11:11:00Z",
  
  "expiry_rules": {
    "session_only": true,
    "expires_at": "NY_CLOSE",
    "invalidate_if_missed_entry": true
  },
  
  "disclaimer": "Not financial advice. Trade responsibly."
}
```

## Telegram Message Format

```
Asset: EUR/USD

📌 Trade: 🟢 BUY (expect price to go up)

⏳ Timeframe: 15-Minute (M15)
🌍 Session: London → New York Overlap

💰 Price Levels:
• Entry Zone: 1.16710 – 1.16750
• Take Profit (TP): 1.17080
• Stop Loss (SL): 1.16480

📏 Trade Details:
• Target: +35 pips
• Risk–Reward: 1 : 1.40
• Suggested Risk: 0.5% – 1% per trade

🕒 Trade Type: Intraday
🧠 AI Confidence: 96% ⭐

⏰ Posted: Jan 13, 2026 — 11:11 UTC

⏳ Auto-Expiry Rules:
• Signal is valid for this session only
• Expires at New York close or if TP or SL is hit
• Do not enter if price has already moved significantly beyond the entry zone

—
⚠️ Not financial advice. Trade responsibly.
```

## Field Definitions

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `asset` | string | Trading pair | "EUR/USD" |
| `direction` | string | Trade direction | "BUY" or "SELL" |
| `direction_icon` | string | Visual indicator | "🟢" (BUY) or "🔴" (SELL) |
| `timeframe` | string | Chart timeframe | "M15" |
| `session` | string | Trading session | "London → New York Overlap" |
| `confidence` | number | AI confidence (0-100) | 96 |
| `posted_at_utc` | string | ISO 8601 timestamp | "2026-01-13T11:11:00Z" |

### Price Levels

| Field | Type | Description |
|-------|------|-------------|
| `entry_zone` | array[string] | Entry price range [min, max] |
| `take_profit` | string | Target exit price |
| `stop_loss` | string | Risk exit price |

### Trade Details

| Field | Type | Description |
|-------|------|-------------|
| `target_pips` | number | Expected profit in pips |
| `risk_reward` | string | Risk-reward ratio |
| `suggested_risk` | string | Recommended risk per trade |

### Expiry Rules

| Field | Type | Description |
|-------|------|-------------|
| `session_only` | boolean | Valid for current session only |
| `expires_at` | string | Expiry condition |
| `invalidate_if_missed_entry` | boolean | Invalidate if price moves past entry |

## Signal Generation Rules

### Confidence Threshold

```
IF confidence >= 95%
  → PUBLISH SIGNAL
ELSE
  → NO SIGNAL
```

### Session Filter

Only publish signals during:
- London session (08:00-17:00 UTC)
- New York session (13:00-22:00 UTC)
- Overlap (13:00-17:00 UTC) ⭐ PREFERRED

### Frequency Limit

- **Web**: Auto-refresh every 10 seconds
- **Telegram**: Maximum 1 signal per asset per day
- **API**: No rate limit on reads, but signals update max once per session

## Direction Mapping

| Direction | Icon | Expectation |
|-----------|------|-------------|
| BUY | 🟢 | Expect price to go up |
| SELL | 🔴 | Expect price to go down |

## Disclaimer

**MUST be included in all signals:**

> ⚠️ Not financial advice. Trade responsibly.

## Examples

### BUY Signal

```json
{
  "asset": "EUR/USD",
  "direction": "BUY",
  "direction_icon": "🟢",
  "confidence": 96
}
```

### SELL Signal

```json
{
  "asset": "EUR/USD",
  "direction": "SELL",
  "direction_icon": "🔴",
  "confidence": 97
}
```

### No Signal (Low Confidence)

```json
{
  "confidence": 82,
  "message": "No high-confidence signal available"
}
```

## Validation Rules

1. ✅ Confidence must be 0-100
2. ✅ Direction must be "BUY" or "SELL"
3. ✅ Entry zone must have 2 prices
4. ✅ Take profit must be beyond entry zone
5. ✅ Stop loss must be opposite side of entry
6. ✅ Posted time must be valid ISO 8601
7. ✅ All prices must be valid numbers

## Version History

- **v1.0** (2026-01-15): Initial template based on Quantix MVP standard
