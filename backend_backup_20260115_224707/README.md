# Signal Genius AI - Backend API

FastAPI backend connecting to Quantix AI Core and Supabase database.

## Architecture

```
Frontend (GitHub Pages)
    ↓
Backend API (Railway/FastAPI) ← YOU ARE HERE
    ↓
Quantix AI Core (Signal Engine)
    ↓
Supabase (Database)
```

## Features

- ✅ **Quantix AI Core Integration** - Fetch high-confidence signals
- ✅ **Confidence Filtering** - Only signals ≥95% confidence
- ✅ **TTL Caching** - 15-minute cache to reduce API calls
- ✅ **Supabase Integration** - Save signals to database
- ✅ **Fallback Mock Data** - Graceful degradation if Quantix unavailable
- ✅ **CORS Enabled** - Allow frontend access
- ✅ **Health Check** - Monitor API status

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required variables:
- `QUANTIX_CORE_BASE_URL` - Quantix AI Core API URL
- `QUANTIX_API_KEY` - Your Quantix API key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Your Supabase service key

### 3. Run Locally

```bash
python main.py
```

Server will start at: `http://localhost:8000`

### 4. Test API

```bash
# Health check
curl http://localhost:8000/health

# Get latest signal
curl http://localhost:8000/api/v1/signal/latest?asset=EUR/USD

# Get active signals from database
curl http://localhost:8000/api/v1/signals/active?limit=10
```

## API Endpoints

### GET `/`
Root endpoint with API info

### GET `/health`
Health check endpoint

### GET `/api/v1/signal/latest`
Get latest high-confidence signal

**Query Parameters:**
- `asset` (optional): Trading asset, default: "EUR/USD"

**Response:**
```json
{
  "asset": "EUR/USD",
  "trade": "BUY",
  "entry": [1.16710, 1.16750],
  "tp": 1.17080,
  "sl": 1.16480,
  "confidence": 96,
  "target_pips": 35,
  "risk_reward": "1 : 1.40",
  "posted_at": "2026-01-15T08:00:00Z",
  "expires_in": 900,
  "source": "quantix"
}
```

### GET `/api/v1/signals/active`
Get active signals from database

**Query Parameters:**
- `limit` (optional): Number of signals, default: 10, max: 100

### GET `/api/v1/lab/market-reference`
Legacy endpoint for backward compatibility

**Query Parameters:**
- `symbol`: Symbol (e.g., "EURUSD")
- `tf`: Timeframe (e.g., "M15")

## Deployment

### Railway

1. Create new project on Railway
2. Connect GitHub repository
3. Set root directory to `/backend`
4. Add environment variables
5. Deploy

### Environment Variables (Railway)

```
QUANTIX_CORE_BASE_URL=https://your-quantix-api.com
QUANTIX_API_KEY=your_key_here
SIGNAL_CONFIDENCE_THRESHOLD=0.95
SIGNAL_TTL_SECONDS=900
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your_key_here
PORT=8000
```

## Project Structure

```
backend/
├── main.py                      # FastAPI app
├── services/
│   ├── __init__.py
│   ├── quantix_client.py       # Quantix AI Core client
│   ├── signal_service.py       # Business logic & caching
│   └── supabase_client.py      # Database operations
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## Development

### Run with Auto-Reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### View API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Logging

The API logs to console. In production, configure proper logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Configuration

### Confidence Threshold

Minimum AI confidence to publish signal (default: 0.95 = 95%)

```
SIGNAL_CONFIDENCE_THRESHOLD=0.95
```

### Cache TTL

How long to cache signals in seconds (default: 900 = 15 minutes)

```
SIGNAL_TTL_SECONDS=900
```

## Error Handling

- **Quantix API Down**: Returns cached signal or mock data
- **Low Confidence**: Returns `{"status": "no_signal"}`
- **Database Error**: Logs error, continues without saving

## Security

- ✅ API keys in environment variables
- ✅ CORS restricted to known origins
- ✅ No sensitive data in responses
- ✅ Supabase RLS enabled

## Monitoring

Check health endpoint regularly:

```bash
curl https://your-api.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T08:00:00Z",
  "service": "signal-genius-ai-api"
}
```

## Troubleshooting

### API returns mock data

- Check `QUANTIX_CORE_BASE_URL` is correct
- Verify `QUANTIX_API_KEY` is valid
- Check Quantix AI Core is running

### Database not saving

- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- Check Supabase tables exist
- Review logs for errors

### CORS errors

- Add your frontend URL to `allow_origins` in `main.py`

## License

© 2026 Signal Genius AI
