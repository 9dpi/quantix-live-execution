# 🚀 Signal Genius AI - MVP v0

## 📋 Overview

Minimal MVP backend for Signal Genius AI - connects frontend to Quantix AI Core.

**Architecture:**
```
Frontend (GitHub Pages) → Backend (Railway) → Quantix AI Core → Response
```

## 🎯 What This MVP Does

- ✅ Provides `/health` endpoint
- ✅ Provides `/api/v1/signal/latest` endpoint
- ✅ Fetches signals from Quantix AI Core
- ✅ Handles CORS for frontend
- ✅ Returns JSON responses
- ✅ Has fallback to mock data

## 📦 Structure

```
backend/
├── main.py              # FastAPI app (minimal)
├── external_client.py   # Quantix API client
└── requirements.txt     # Dependencies (4 packages only)
```

## 🔧 Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - HTTP client
- `python-dotenv` - Environment variables

**No Database. No Workers. No Extra Complexity.**

## 🚀 Local Development

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run server
cd backend
python main.py
```

Server runs on `http://localhost:8000`

## 🧪 Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get latest signal
curl http://localhost:8000/api/v1/signal/latest
```

## 🌐 Railway Deployment

1. Push to GitHub
2. Railway auto-deploys
3. Test endpoints:
   ```bash
   curl https://[your-app].railway.app/health
   curl https://[your-app].railway.app/api/v1/signal/latest
   ```

## ✅ MVP Checklist

- [x] Backend minimal code
- [x] No database
- [x] No workers
- [x] CORS enabled
- [x] Health check works
- [x] Signal endpoint works
- [x] Fallback to mock data
- [ ] Railway deployed
- [ ] Frontend connected
- [ ] Data displays

## 🎯 Next Steps (After MVP Works)

1. Add confidence filter
2. Add caching
3. Add database (optional)
4. Add Telegram bot (optional)

## 📝 Notes

- This is MVP v0 - intentionally minimal
- Focus: **Working > Perfect**
- Principle: **Data > Design**
- Goal: **Frontend displays data**

---

**Status:** 🟡 Ready for deployment  
**Version:** 0.1.0  
**Date:** 2026-01-15
