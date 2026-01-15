"""
Signal Genius AI - Minimal MVP Backend
Simple FastAPI backend connecting Frontend to Quantix AI Core
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from external_client import fetch_signal
import os

# Initialize FastAPI app
app = FastAPI(
    title="Signal Genius AI - MVP",
    description="Minimal backend for EUR/USD trading signals",
    version="0.1.0"
)

# CORS middleware - Allow all origins for MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for MVP simplicity
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
        "name": "Signal Genius AI - MVP",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "latest_signal": "/api/v1/signal/latest"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "signal-genius-ai-mvp"
    }

# =====================================================
# Signal Endpoint
# =====================================================

@app.get("/api/v1/signal/latest")
def latest(asset: str = Query("EUR/USD", description="Trading asset")):
    """
    Get latest signal from Quantix AI Core
    
    Simple pass-through endpoint:
    Frontend → This API → Quantix API → Response
    """
    try:
        # Fetch from external API
        payload = fetch_signal(asset)
        
        return {
            "status": "ok",
            "source": "external",
            "asset": asset,
            "payload": payload
        }
        
    except Exception as e:
        # Simple error handling - return error but don't crash
        return {
            "status": "error",
            "message": str(e),
            "asset": asset
        }

# =====================================================
# Run Server
# =====================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
