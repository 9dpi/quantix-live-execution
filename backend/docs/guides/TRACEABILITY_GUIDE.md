# 🧾 Signal Traceability & Lifecycle System

## 🎯 Purpose

Every signal has:
- **Unique Identity** (Signal ID)
- **Defined Lifespan** (Expiry)
- **Clear Status** (Active/Closed)
- **Auditable History** (For statistics)

This is what separates a professional trading system from a toy project.

## 🆔 Signal ID Format

### Structure
```
SIG-{SYMBOL}-{YYYYMMDD}-{HHMM}
```

### Examples
```
SIG-EURUSD-20260116-1530
SIG-GBPUSD-20260116-0945
SIG-USDJPY-20260117-2200
```

### Properties
- **Unique**: One ID per signal
- **Immutable**: Never changes
- **Consistent**: Same across Web, Telegram, Logs, DB
- **Human-readable**: Easy to reference in support

## ⏰ Expiry System

### Time-based Expiry
```json
{
  "expiry": {
    "type": "time",
    "expires_at": "2026-01-16T16:30:00Z"
  }
}
```

### Bar-based Expiry (Future)
```json
{
  "expiry": {
    "type": "bars",
    "bars": 3,
    "timeframe": "M15"
  }
}
```

### Why Expiry Matters
- Traders know when signal is no longer valid
- Prevents confusion about old signals
- Enables automatic cleanup
- Required for accurate win/loss tracking

## 📊 Signal Status

### Status Enum
| Status | Meaning | When Set |
|--------|---------|----------|
| `ACTIVE` | Signal is live | On generation |
| `HIT_TP` | Take profit reached | Price monitoring |
| `HIT_SL` | Stop loss hit | Price monitoring |
| `EXPIRED` | Time/bars expired | Expiry check |
| `CANCELLED` | Manually cancelled | Admin action |

### Status Flow
```
ACTIVE → HIT_TP (WIN)
      → HIT_SL (LOSS)
      → EXPIRED (NO TRADE)
      → CANCELLED (RARE)
```

## 📋 Complete Signal Payload

### Full Example
```json
{
  "signal_id": "SIG-EURUSD-20260116-1530",
  "status": "ACTIVE",
  "symbol": "EUR/USD",
  "direction": "BUY",
  "entry": 1.0845,
  "tp": 1.0890,
  "sl": 1.0810,
  "confidence": 88,
  "confidence_meta": {
    "tier": "HIGH",
    "telegram": true,
    "label": "⭐ High Confidence"
  },
  "strategy": "EMA Trend + RSI + ATR",
  "timeframe": "M15",
  "session": "London-NewYork",
  "generated_at": "2026-01-16T15:30:00Z",
  "expiry": {
    "type": "time",
    "expires_at": "2026-01-16T16:30:00Z"
  },
  "source": "rule-engine",
  "market": "real"
}
```

## 📱 Telegram Display

### VIP Message with Traceability
```
🚨 TRADE SIGNAL – HIGH CONFIDENCE

🆔 Signal ID: SIG-EURUSD-20260116-1530
📊 EUR/USD (M15)
🟢 Action: BUY
🎯 Entry: 1.0845
🎯 TP: 1.0890
🛑 SL: 1.0810

⭐ Confidence: 88% (HIGH)
🧠 Strategy: EMA Trend + RSI + ATR
⏰ Expires at: 16:30 UTC

⚠️ Risk: Medium
📌 Manage position size carefully
```

## 📈 Future Capabilities

### 1. Outcome Tracking
```json
{
  "signal_id": "SIG-EURUSD-20260116-1530",
  "status": "HIT_TP",
  "outcome": {
    "result": "WIN",
    "pips": 45,
    "closed_at": "2026-01-16T16:10:00Z",
    "duration_minutes": 40
  }
}
```

### 2. Follow-up Messages
```
✅ Signal SIG-EURUSD-20260116-1530
🎯 RESULT: WIN (+45 pips)
⏱️ Duration: 40 minutes
💰 Risk:Reward achieved: 1:1.8
```

### 3. Performance Dashboard
```
📊 Last 30 Days Performance

Total Signals: 45
Win Rate: 67% (30W / 15L)
Avg Win: +38 pips
Avg Loss: -22 pips
Best Signal: SIG-EURUSD-20260110-0930 (+85 pips)

By Tier:
  HIGH (≥85%): 72% win rate
  MEDIUM (60-84%): 58% win rate
```

### 4. Audit Trail
```sql
SELECT 
  signal_id,
  symbol,
  direction,
  confidence,
  status,
  outcome_result,
  generated_at,
  closed_at
FROM signals
WHERE generated_at >= '2026-01-01'
ORDER BY generated_at DESC;
```

## 🛡️ Data Retention

### Recommended Policy
- **Active signals**: Keep indefinitely
- **Closed signals**: Keep for 1 year
- **Logs**: Keep for 90 days
- **Statistics**: Aggregate monthly

### Storage Needs
- Average signal: ~1KB JSON
- 100 signals/day = 100KB/day
- 1 year = ~36MB (negligible)

## 🎯 Business Impact

### Trust Building
- "We track every signal we send"
- "Here's our verified track record"
- "You can audit any signal by ID"

### Marketing
- Share win screenshots with Signal ID
- Publish monthly performance reports
- Prove system consistency over time

### Support
- "Please reference Signal ID: SIG-XXX"
- Quick lookup for customer questions
- Dispute resolution with proof

### Product Development
- Identify which strategies work best
- A/B test different confidence thresholds
- Optimize based on real outcomes

## 🔧 Implementation Checklist

- [x] Generate unique Signal IDs
- [x] Add expiry structure to payload
- [x] Set initial status to ACTIVE
- [x] Display Signal ID in Telegram
- [x] Show expiry time to users
- [ ] Implement outcome tracking (Phase 2)
- [ ] Build performance dashboard (Phase 2)
- [ ] Add database persistence (Phase 2)
- [ ] Create audit API (Phase 2)

## 💡 Key Principle

> "Every signal is a promise. Track it. Own it. Prove it."

This is what transforms an AI experiment into a professional trading service that customers trust and pay for.
