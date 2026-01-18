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
async def observability_and_guard(request: Request, call_next):
    # Log mỗi request
    print(f"📡 [{request.method}] {request.url.path}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {repr(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal Execution Error"}
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    # always 200
    return {"status": "ok"}

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
async def telegram_webhook(request: Request):
    """
    STRICT TELEGRAM WEBHOOK PROTOCOL:
    1. POST only (Checked by FastAPI)
    2. Never block/sync
    3. Never crash on malformed payloads
    4. Always return 200 OK to Telegram
    """
    try:
        data = await request.json()
    except:
        return {"ok": True} # Trả về OK ngay cả khi payload không phải JSON chuẩn

    # Log sơ bộ để quan sát
    print(f"📥 Telegram Webhook: {data.get('update_id')}")

    try:
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if not chat_id or not text:
            return {"ok": True}

        if text.startswith("/signal"):
            # Lấy tín hiệu cuối cùng (Frozen)
            # Không dùng get_latest_signal_safe() để tránh sinh signal mới vô ý
            from main import CURRENT_SIGNAL
            if CURRENT_SIGNAL:
                send_telegram(chat_id, CURRENT_SIGNAL)
            else:
                send_simple_message(chat_id, "⏳ No signal executed yet. Check dashboard.")
            
        elif text.startswith("/start") or text.startswith("/help"):
            welcome_msg = (
                "🚀 *Quantix Live Bot*\n\n"
                "I follow the ONE signal - ONE execution protocol.\n\n"
                "/signal - Get the frozen live signal"
            )
            send_simple_message(chat_id, welcome_msg)

    except Exception as e:
        print(f"⚠️ Webhook logic error (Suppressed): {e}")
    
    return {"status": "received", "ok": True}

def send_simple_message(chat_id, text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token: return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id, 
        "text": text,
        "parse_mode": "Markdown"
    })
