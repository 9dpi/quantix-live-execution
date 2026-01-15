from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.external_client import fetch_candles
from backend.signal_engine import generate_signal

app = FastAPI(title="Signal Genius AI MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/signal/latest")
async def latest_signal():
    try:
        candles = await fetch_candles()
        signal = generate_signal(candles)
        # Wrap signal in payload to match FE expectations
        return {
            "status": "ok",
            "payload": signal
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
