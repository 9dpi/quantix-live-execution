# Quantix Signal Genius AI - System Architecture (2026-02-06)

## 🏗️ All-on-Cloud Architecture Overview (v3.0)

Quantix now operates a **Full Cloud Architecture** on Railway:
- **Data Ingestion & Analysis**: Cloud (Railway - Analyzer Service) ☁️
- **Monitoring & Lifecycle**: Cloud (Railway - Watcher Service) [Binance Data Feed] ☁️
- **Storage & distribution**: Cloud (Supabase + Railway API) ☁️

*Note: Home Miner (Local) is now decommissioned and acts only as a manual backup.*

---

## 📊 Complete Signal Flow

```
[T0] Live Market Data (Binance EURUSDT WebSocket/REST)
     ↓ (Zero-latency / Real-time)
     
[T0+Δ] QUANTIX AI CORE - Home Miner 🏠
├─ Location: Local Machine (Residential IP)
├─ Repo: github.com/9dpi/quantix-ai-core
├─ Function: ContinuousAnalyzer
│  ├─ Fetch EURUSD M15 data
│  ├─ Structure Analysis (StructureEngineV1)
│  ├─ Confidence Calculation (0.0 - 1.0)
│  └─ Strength Calculation (0.0 - 1.0)
├─ Decision Logic:
│  ├─ Confidence >= 95% → ULTRA Signal (Auto-push Telegram)
│  ├─ Confidence >= 75% → ACTIVE Signal (Lock to DB)
│  └─ Confidence < 75%  → CANDIDATE (Temporary)
└─ Output: Signal Object
     ↓ (HTTPS POST)
     
[T1] SUPABASE CLOUD DATABASE ☁️
├─ Table: fx_signals
├─ Status Types:
│  ├─ ACTIVE: Valid signal ready for execution
│  ├─ CANDIDATE: Low confidence (auto-purged after 1h)
│  └─ EXPIRED: Past validity window
├─ Key Fields:
│  ├─ asset, direction, timeframe
│  ├─ entry_low, tp, sl
│  ├─ ai_confidence (0.0-1.0)
│  ├─ strength (0.0-1.0)
│  └─ generated_at, status
└─ Immutable Append-Only Log
     ↓
     ├──────────────────────┬──────────────────────┐
     ↓                      ↓                      ↓
     
[T2] TELEGRAM BOT         [T2] WEB DASHBOARD    [T2] LIVE EXECUTION
├─ Proactive Push         ├─ Railway Hosted     ├─ Signal Consumer
│  (AI Core Direct)       ├─ signalgeniusai.com ├─ Reads Supabase
├─ Webhook Handler        ├─ Reads Supabase     └─ Executes Trades
│  (/signal command)      └─ Real-time Display       (Demo/Live)
└─ 3 Templates:
   ├─ ⚡️ ACTIVE (Standard)
   ├─ 🚨 ULTRA (95%+)
   └─ ⛔ EXPIRED (Record)
```

---

## 📱 Telegram Message Templates

### Template 1: ACTIVE Signal (Standard)
```
⚡️ SIGNAL GENIUS AI

Asset: EURUSD
Timeframe: M15
Direction: 🔴 SELL

Status: 🟢 ACTIVE
Valid for: ~78 minutes

Confidence: 87%
Force/Strength: 63%

🎯 Entry: 1.19498
💰 TP: 1.19298
🛑 SL: 1.19648
```

### Template 2: ULTRA Signal (95%+)
```
🚨 ULTRA SIGNAL (95%+)

EURUSD | M15
🔴 SELL

Status: 🟢 ACTIVE
Entry window: OPEN

Confidence: 97%
Strength: 91%

🎯 Entry: 1.19498
💰 TP: 1.19298
🛑 SL: 1.19648
```

### Template 3: EXPIRED Signal (Record)
```
⚡️ SIGNAL GENIUS AI

Asset: EURUSD
Timeframe: M15
Direction: 🔴 SELL

Status: ⛔ EXPIRED (for record only)

Entry: 1.19498
TP: 1.19298
SL: 1.19648

Result: TP hit / SL hit / Closed
```

---

## 🔐 Security & Reliability

### Deduplication Mechanisms
1. **Daily Cap**: Max 1 ACTIVE signal per day (enforced by `has_traded_today()`)
2. **Cooldown**: 60-minute gap between Telegram pushes
3. **Signal Fingerprint**: Prevents duplicate messages (asset + direction + entry)

### Fail-Safe Features
- **Local Heartbeat Log**: `heartbeat_audit.jsonl` (survives restarts)
- **Cloud Telemetry**: `fx_analysis_log` table (persistent monitoring)
- **Graceful Degradation**: System continues if DB temporarily unavailable

---

## 🎯 Trading Rules (AUTO v0)

### Fixed Risk/Reward Rule
**Effective**: 2026-01-30  
**Version**: AUTO v0

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Take Profit (TP)** | 10 pips | Fixed for all signals |
| **Stop Loss (SL)** | 10 pips | Fixed for all signals |
| **Risk/Reward Ratio** | 1:1 | Fixed ratio |

#### Application Scope
- ✅ Applies to **100% of all signals**
- ✅ **DOES NOT** change based on:
  - Market condition (trending/ranging)
  - Confidence level (75%, 95%+)
  - Volatility (ATR, Bollinger Bands)
  - Timeframe (M1, M5, M15, H1)

#### Examples
```
BUY Signal:
Entry: 1.19500
TP:    1.19600 (+10 pips)
SL:    1.19400 (-10 pips)

SELL Signal:
Entry: 1.19500
TP:    1.19400 (-10 pips)
SL:    1.19600 (+10 pips)
```

#### Rationale
- **Simplicity**: Easy to understand and implement
- **Consistency**: Uniform risk profile across all signals
- **Backtesting**: Standardized parameters for performance evaluation
- **Risk Management**: Clear, predictable risk per trade

**Documentation**: See `FIXED_RR_RULE_v0.md` for full specification

---

## 📦 Repository Structure

```
Quantix_AI_Core/              (Home Miner - Local)
├─ backend/
│  ├─ quantix_core/
│  │  ├─ engine/
│  │  │  └─ continuous_analyzer.py  ← Main Heartbeat
│  │  ├─ ingestion/
│  │  │  └─ twelve_data_client.py
│  │  └─ api/
│  │     └─ main.py  ← Railway API (Optional)
│  └─ requirements.txt
└─ Dockerfile

quantix-live-execution/       (Execution Layer)
├─ signal_engine.py           ← Supabase Consumer
├─ telegram_formatter.py      ← 3 Templates
└─ main.py                    ← FastAPI Server

Signal_Genius_AI/             (Web Dashboard)
├─ backend/
│  ├─ main.py                 ← Webhook Handler
│  └─ telegram_formatter.py   ← 3 Templates
└─ frontend/
   └─ index.html              ← GitHub Pages
```

---

## 🚀 Deployment Status

| Component | Location | Status | URL |
|-----------|----------|--------|-----|
| AI Core (Miner) | Local Machine | 🟢 Running | localhost:8000 |
| AI Core (API) | Railway | 🟢 Online | quantixapiserver-production.up.railway.app |
| Web Dashboard | Railway | 🟢 Online | signalgeniusai-production.up.railway.app |
| Frontend | GitHub Pages | 🟢 Live | www.signalgeniusai.com |
| Database | Supabase | 🟢 Connected | Cloud Postgres |

---

**Last Updated**: 2026-01-30  
**Architecture Version**: 3.1 (Railway Watcher + Binance Feed + 35m Lifecycle)  
**Status**: ✅ Production Ready


