# Signal Genius AI - Backend API
# FastAPI backend connecting to Quantix AI Core

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime, timezone
from typing import Optional
import uvicorn

# Import services
from backend.services.quantix_client import fetch_quantix_signal
from backend.services.signal_service import get_latest_signal
from backend.core.supabase_client import init_supabase, save_signal_to_db, get_active_signals, is_db_connected

# Initialize FastAPI app
app = FastAPI(
    title="Signal Genius AI API",
    description="Professional EUR/USD Forex Trading Signals powered by Quantix AI Core",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize core services on startup"""
    init_supabase()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://9dpi.github.io",
        "https://9dpi.github.io/signal-genius-ai",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# Health Check
# =====================================================

@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "name": "Signal Genius AI API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "latest_signal": "/api/v1/signal/latest",
            "active_signals": "/api/v1/signals/active"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint with DB status"""
    
    db_status = "connected" if is_db_connected() else "disconnected"
    
    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "signal-genius-ai-api"
    }

# =====================================================
# Signal Endpoints
# =====================================================

@app.get("/api/v1/signal/latest")
def latest_signal(asset: str = Query("EUR/USD", description="Trading asset")):
    """
    Primary endpoint for high-confidence AI signals
    
    - Calls Quantix AI Core reference
    - Validates data through Confidence Gate (≥95%)
    - Caches snapshot (TTL = 15m)
    - Logs to Supabase Data Layer (Optional)
    - Returns unified rich format
    """
    # FIX 1: Fail-safe check
    if not is_db_connected():
        try:
            signal = get_latest_signal(asset)
            if signal.get("status") != "no_signal":
                # Thêm thông tin degraded mode nhưng vẫn trả về signal
                signal["status_db"] = "disconnected"
                signal["mode"] = "reference-only"
                return signal
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "degraded",
                    "message": "Database unavailable, running in reference-only mode",
                    "source": "quantix",
                }
            )
        except Exception:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "degraded",
                    "message": "Database unavailable, running in reference-only mode",
                    "source": "quantix",
                }
            )

    try:
        signal = get_latest_signal(asset)
        
        # If no signal (low confidence)
        if signal.get("status") == "no_signal":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "no_signal",
                    "message": "No actionable signal available",
                    "confidence": signal.get("confidence", 0),
                    "threshold": 85
                }
            )
        
        # FIX 2: Tách DB khỏi critical path
        if signal.get("source") == "quantix":
            try:
                save_signal_to_db(signal)
            except Exception as e:
                # Log lỗi nhưng không làm crash app
                print(f"DEBUG: Supabase save failed: {e}")
        
        return signal
        
    except Exception as e:
        # API không bao giờ được 500 vì infra
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Service encountered an issue: {str(e)}",
                "source": "fail-safe"
            }
        )

@app.get("/api/v1/signals/active")
def active_signals(limit: int = Query(10, ge=1, le=100)):
    """
    Get active signals from database
    
    - Returns signals with is_active=true
    - Ordered by created_at DESC
    - Limit: 1-100 signals
    """
    # Fail-safe: Check DB connection first
    if not is_db_connected():
        return JSONResponse(
            status_code=200,
            content={
                "status": "degraded",
                "message": "Database unavailable",
                "count": 0,
                "signals": []
            }
        )
    
    try:
        signals = get_active_signals(limit)
        return {
            "status": "ok",
            "count": len(signals),
            "signals": signals
        }
    except Exception as e:
        # Never crash - return empty list with error info
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Failed to fetch signals: {str(e)}",
                "count": 0,
                "signals": []
            }
        )

# =====================================================
# Legacy Endpoint (for compatibility)
# =====================================================

@app.get("/api/v1/lab/market-reference")
def market_reference(
    symbol: str = Query("EURUSD", description="Symbol (e.g., EURUSD)"),
    tf: str = Query("M15", description="Timeframe")
):
    """
    Legacy endpoint for backward compatibility
    """
    # Convert EURUSD to EUR/USD format if needed
    asset = f"{symbol[:3]}/{symbol[3:]}" if len(symbol) == 6 and "/" not in symbol else symbol
    
    signal = get_latest_signal(asset)
    
    if signal.get("status") == "no_signal":
        return JSONResponse(
            status_code=200,
            content={
                "message": "No high-confidence signal available",
                "confidence": signal.get("confidence", 0)
            }
        )
    
    return signal

# =====================================================
# Run Server
# =====================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
