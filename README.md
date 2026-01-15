# 🚀 Signal Genius AI

**Professional EUR/USD Forex Trading Signals powered by Advanced AI**

![License](https://img.shields.io/badge/license-Proprietary-blue)
![Status](https://img.shields.io/badge/status-MVP-green)
![Confidence](https://img.shields.io/badge/min%20confidence-95%25-brightgreen)

---

## 🎯 Overview

Signal Genius AI is a professional forex signal platform that analyzes EUR/USD market conditions using advanced AI algorithms. The system only publishes signals when AI confidence reaches **95% or higher**, ensuring quality over quantity.

### Key Features

- ✅ **High Confidence Only**: Signals published only when AI confidence ≥ 95%
- ✅ **Real-Time Updates**: Web interface auto-refreshes every 10 seconds
- ✅ **Telegram Integration**: One high-quality signal per day via Telegram
- ✅ **Mobile-First Design**: Beautiful Bento UI optimized for all devices
- ✅ **Clear Risk Management**: Every signal includes entry, TP, SL, and risk-reward ratio
- ✅ **Auto-Expiry Rules**: Signals expire at session close or when targets are hit

---

## 📊 Trading Specifications

| Parameter | Value |
|-----------|-------|
| **Asset** | EUR/USD |
| **Timeframe** | M15 (15-minute) |
| **Sessions** | London, New York, Overlap |
| **Min Confidence** | 95% |
| **Signals per Day** | 1 (Telegram), Unlimited (Web) |
| **Auto-Refresh** | 10 seconds (Web) |

---

## 🏗️ Architecture

```
Signal Genius AI Core (Backend API)
         │
         ▼
/api/v1/lab/market-reference (JSON)
         │
         ├── Web MVP (Auto-refresh 10s)
         └── Telegram Bot (1 signal/day)
```

### Components

1. **Frontend** (`/frontend`)
   - Modern Bento UI design
   - Auto-refresh every 10 seconds
   - Mobile-first responsive layout
   - Real-time signal display

2. **Telegram Bot** (`/telegram`)
   - Sends 1 signal per day
   - Confidence threshold: 95%
   - Checks API every 15 minutes
   - Plain text format

3. **Documentation** (`/docs`)
   - Signal template specification
   - API contract
   - Deployment guides

---

## 🚀 Quick Start

### Frontend (Web)

1. **Open the web interface:**
   ```bash
   cd frontend
   # Open index.html in browser or use a local server
   python -m http.server 8080
   ```

2. **Visit:** `http://localhost:8080`

3. **Features:**
   - View current signal (if confidence ≥ 95%)
   - Auto-refresh every 10 seconds
   - Mobile-responsive design

### Telegram Bot

1. **Install dependencies:**
   ```bash
   cd telegram
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token
   export TELEGRAM_CHAT_ID=your_chat_id
   export API_ENDPOINT=http://your-api-url/api/v1/lab/market-reference
   ```

3. **Run the bot:**
   ```bash
   python bot.py
   ```

See [telegram/README.md](telegram/README.md) for detailed setup instructions.

---

## 📱 Signal Format

Every signal includes:

- **Asset & Direction**: EUR/USD BUY/SELL
- **Timeframe & Session**: M15, London/NY
- **Price Levels**: Entry Zone, Take Profit, Stop Loss
- **Trade Details**: Target pips, Risk-Reward, Suggested risk
- **AI Confidence**: Percentage score
- **Expiry Rules**: Session-based expiration

See [docs/SIGNAL_TEMPLATE.md](docs/SIGNAL_TEMPLATE.md) for complete specification.

---

## 🎨 Design Philosophy

### Bento UI

Signal Genius AI uses a modern **Bento UI** design system:

- **Clean & Minimal**: Focus on essential information
- **Card-Based Layout**: Organized, scannable content
- **Dark Theme**: Reduced eye strain, professional look
- **Smooth Animations**: Micro-interactions for better UX
- **Mobile-First**: Optimized for all screen sizes

### Color Palette

- **Primary Blue**: `#0066ff` - Trust, stability
- **Primary Cyan**: `#00d4ff` - Technology, innovation
- **Accent Green**: `#00ff88` - Success, profit
- **Dark Background**: `#0a0e1a` - Premium, focus

---

## 🔧 API Contract

### Endpoint

```
GET /api/v1/lab/market-reference
```

### Query Parameters

```
?symbol=EURUSD&tf=M15
```

### Response Schema

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

---

## 📈 Deployment

### Frontend (GitHub Pages)

```bash
# Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# Enable GitHub Pages
# Settings → Pages → Source: main branch → /frontend
```

### Backend (Railway)

```bash
# Deploy to Railway
railway login
railway init
railway up
```

### Telegram Bot (Railway/Fly.io)

See [telegram/README.md](telegram/README.md) for deployment instructions.

---

## 🛡️ Risk Disclaimer

**IMPORTANT**: Signal Genius AI provides AI-generated market references for **educational purposes only**.

- ⚠️ This is **NOT financial advice**
- ⚠️ Trading involves **significant risk**
- ⚠️ Users are **fully responsible** for their trading decisions
- ⚠️ Past performance does **NOT guarantee** future results
- ⚠️ Only trade with money you can **afford to lose**

---

## 📋 Roadmap

### Phase 1: MVP ✅
- [x] Frontend with Bento UI
- [x] Auto-refresh (10s)
- [x] Telegram bot
- [x] Signal template
- [x] Documentation

### Phase 2: Backend (In Progress)
- [ ] FastAPI backend
- [ ] Real-time market data integration
- [ ] AI signal generation engine
- [ ] Database for signal history

### Phase 3: Enhancement
- [ ] Multi-asset support (GBP/USD, USD/JPY, etc.)
- [ ] Multiple timeframes (M5, M30, H1)
- [ ] Performance tracking
- [ ] User authentication
- [ ] Premium features

---

## 🤝 Support

For questions or support:
- 📧 Email: support@signalgenius.ai
- 💬 Telegram: @SignalGeniusSupport
- 📚 Documentation: [docs/](docs/)

---

## 📄 License

© 2026 Signal Genius AI. All rights reserved.

This is proprietary software. Unauthorized copying, distribution, or modification is strictly prohibited.

---

## 🙏 Acknowledgments

Built with:
- Modern web technologies (HTML5, CSS3, JavaScript)
- Python & Telegram Bot API
- Inspired by Quantix MVP architecture

---

**Made with ❤️ by Signal Genius AI Team**
