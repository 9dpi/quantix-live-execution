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
from services.quantix_client import fetch_quantix_signal
from services.signal_service import get_latest_signal
from services.supabase_client import save_signal_to_db, get_active_signals

# Initialize FastAPI app
app = FastAPI(
    title="Signal Genius AI API",
    description="Professional EUR/USD Forex Trading Signals powered by Quantix AI Core",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all for troubleshooting
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "signal-genius-ai-api"
    }

# =====================================================
# Signal Endpoints
# =====================================================

@app.get("/api/v1/signal/latest")
def latest_signal(asset: str = Query("EUR/USD", description="Trading asset")):
    """
    Get latest high-confidence signal for specified asset
    
    - Calls Quantix AI Core
    - Applies confidence threshold (≥95%)
    - Returns cached signal if within TTL
    - Saves to Supabase database
    """
    try:
        signal = get_latest_signal(asset)
        
        # If no signal (low confidence)
        if signal.get("status") == "no_signal":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "no_signal",
                    "message": "No high-confidence signal available",
                    "confidence": signal.get("confidence", 0),
                    "threshold": 95
                }
            )
        
        # Save to database if new signal
        if signal.get("source") == "quantix":
            save_signal_to_db(signal)
        
        return signal
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch signal: {str(e)}"
        )

@app.get("/api/v1/signals/active")
def active_signals(limit: int = Query(10, ge=1, le=100)):
    """
    Get active signals from database
    
    - Returns signals with is_active=true
    - Ordered by created_at DESC
    - Limit: 1-100 signals
    """
    try:
        signals = get_active_signals(limit)
        return {
            "count": len(signals),
            "signals": signals
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch active signals: {str(e)}"
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
    Maps to latest_signal endpoint
    """
    # Convert EURUSD to EUR/USD format
    asset = f"{symbol[:3]}/{symbol[3:]}" if len(symbol) == 6 else symbol
    
    signal = get_latest_signal(asset)
    
    if signal.get("status") == "no_signal":
        return JSONResponse(
            status_code=200,
            content={
                "message": "No high-confidence signal available",
                "confidence": signal.get("confidence", 0)
            }
        )
    
    # Map to legacy format
    return {
        "asset": signal["asset"],
        "direction": signal["trade"],
        "direction_icon": "🟢" if signal["trade"] == "BUY" else "🔴",
        "timeframe": tf,
        "session": "London → New York Overlap",
        "price_levels": {
            "entry_zone": signal["entry"],
            "take_profit": str(signal["tp"]),
            "stop_loss": str(signal["sl"])
        },
        "trade_details": {
            "target_pips": signal.get("target_pips", 35),
            "risk_reward": signal.get("risk_reward", "1 : 1.40"),
            "suggested_risk": "0.5% – 1%"
        },
        "trade_type": "Intraday",
        "confidence": signal["confidence"],
        "posted_at_utc": signal["posted_at"],
        "expiry_rules": {
            "session_only": True,
            "expires_at": "NY_CLOSE",
            "invalidate_if_missed_entry": True
        },
        "disclaimer": "Not financial advice. Trade responsibly."
    }

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
