from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from signal_engine import get_latest_signal_safe, is_market_open
from telegram_formatter import send_telegram
import os
import requests

app = FastAPI()

# Global History Cache (MPV Simple Ledger)
HISTORY = []
CURRENT_SIGNAL = None  # Live Proof Baseline

@app.middleware("http")
async def global_guard(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("🔥 GLOBAL CRASH PREVENTED:", repr(e))
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Execution Engine Error"}
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "mode": "LIVE_PROOF", "executed": CURRENT_SIGNAL is not None}

@app.get("/signal/latest")
def latest():
    global CURRENT_SIGNAL
    if CURRENT_SIGNAL is None:
        return JSONResponse(
            status_code=404,
            content={"status": "WAITING", "message": "No signal executed yet"}
        )
    return CURRENT_SIGNAL

@app.post("/signal/execute")
def execute():
    """Manually trigger a new signal execution - STRICT ONE-TIME + MARKET GUARD"""
    global CURRENT_SIGNAL
    
    # 1. Market Open Guard
    if not is_market_open():
        return JSONResponse(
            status_code=403,
            content={
                "status": "MARKET_CLOSED",
                "message": "Forex market is currently closed. Execution blocked."
            }
        )

    # 2. Strict One-Time Guard
    if CURRENT_SIGNAL is not None:
        return JSONResponse(
            status_code=409,
            content={
                "status": "ALREADY EXECUTED",
                "message": "Live Proof allows only ONE execution per session",
                "executed_at": CURRENT_SIGNAL.get("executed_at")
            }
        )
    
    # Generate the frozen signal
    sig = get_latest_signal_safe()
    
    # Map to the specific Live Proof format requested
    CURRENT_SIGNAL = {
        "signal_id": f"live-{len(HISTORY) + 1:03d}",
        "status": "EXECUTED",
        "asset": sig["asset"],
        "direction": sig["direction"],
        "entry": sig["entry"],
        "tp": sig["tp"],
        "sl": sig["sl"],
        "confidence": sig["confidence"],
        "executed_at": sig["timestamp"],
        "mode": "LIVE" if os.getenv("LIVE_MODE") == "true" else "SIMULATION"
    }
    
    HISTORY.insert(0, CURRENT_SIGNAL)
    
    # Auto-save to preliminary log
    save_execution_log({
        "signal_id": CURRENT_SIGNAL["signal_id"],
        "executed_at": CURRENT_SIGNAL["executed_at"],
        "market_price": CURRENT_SIGNAL["entry"],
        "status": "PENDING_PROOF"
    })
    
    return CURRENT_SIGNAL

@app.post("/signal/log")
async def log_proof(req: Request):
    """PHASE 5: Commit human-in-the-loop proof (TradingView + Video link)"""
    data = await req.json()
    signal_id = data.get("signal_id")
    
    # Validation
    if not CURRENT_SIGNAL or CURRENT_SIGNAL["signal_id"] != signal_id:
        return JSONResponse(status_code=404, content={"message": "Signal ID not found or not active"})

    log_entry = {
        "signal_id": signal_id,
        "executed_at": CURRENT_SIGNAL["executed_at"],
        "market_price": CURRENT_SIGNAL["entry"],
        "placed_on": data.get("placed_on", "TradingView"),
        "video": data.get("video", "MISSING_LINK"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    save_execution_log(log_entry)
    return {"status": "LOGGED", "entry": log_entry}

def save_execution_log(entry):
    import json
    log_file = "execution_log.json"
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try: logs = json.load(f)
            except: logs = []
    
    # Update if exists, else append
    for i, log in enumerate(logs):
        if log["signal_id"] == entry["signal_id"]:
            logs[i] = entry
            break
    else:
        logs.append(entry)
        
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

@app.get("/signal/history")
def history():
    return HISTORY

@app.get("/signal/stats")
def stats():
    return {
        "total_signals": len(HISTORY),
        "status": "operational",
        "engine": "Quantix AI Core v1.1"
    }

@app.post("/telegram/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        print("📥 Telegram update:", data)

        message = data.get("message")
        if not message:
            return {"ok": True}  # Bỏ qua mọi event khác

        chat = message.get("chat")
        text = message.get("text", "")

        if not chat:
            return {"ok": True}

        chat_id = chat["id"]

        if text.startswith("/signal"):
            signal = get_latest_signal_safe()
            send_telegram(chat_id, signal)
            
        elif text.startswith("/start") or text.startswith("/help"):
            welcome_msg = (
                "🚀 *Signal Genius AI Bot v1.1*\n\n"
                "Welcome trader! I am synced with the Web Dashboard.\n\n"
                "Commands:\n"
                "/signal - Get the latest AI signal\n"
                "/dashboard - Web link"
            )
            send_simple_message(chat_id, welcome_msg)

        return {"ok": True}

    except Exception as e:
        print("❌ TELEGRAM WEBHOOK ERROR:", repr(e))
        return {"ok": True}  # QUAN TRỌNG: KHÔNG ĐƯỢC CRASH

def send_simple_message(chat_id, text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token: return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id, 
        "text": text,
        "parse_mode": "Markdown"
    })
