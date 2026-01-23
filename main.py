from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from signal_engine import get_latest_signal_safe, is_market_open
from telegram_formatter import send_telegram
import os
import json
import requests
from datetime import datetime, timezone

app = FastAPI()

# Only ONE signal allowed per session
def load_persisted_signal():
    try:
        if os.path.exists("execution_log.json"):
            with open("execution_log.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("status") == "EXECUTED":
                    # DAILY RESET: Only load if it was executed today (UTC)
                    exec_at = data.get("executed_at")
                    if exec_at:
                        exec_date = datetime.fromisoformat(exec_at.replace('Z', '+00:00')).strftime("%Y-%m-%d")
                        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                        if exec_date == today:
                            return data
                        else:
                            print(f"♻️ Clearing old signal from {exec_date} (Today: {today})")
    except Exception as e:
        print(f"⚠️ Failed to load persistent log: {e}")
    return None

def get_active_signal():
    """Returns the current signal if it's from today, otherwise clears it."""
    global CURRENT_SIGNAL
    
    if CURRENT_SIGNAL:
        exec_at = CURRENT_SIGNAL.get("executed_at")
        if exec_at:
            exec_date = datetime.fromisoformat(exec_at.replace('Z', '+00:00')).strftime("%Y-%m-%d")
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if exec_date != today:
                print(f"♻️ Resetting session signal from {exec_date}")
                CURRENT_SIGNAL = None
    
    # If still None, try reloading from file (but load_persisted_signal also checks date)
    if CURRENT_SIGNAL is None:
        CURRENT_SIGNAL = load_persisted_signal()
        
    return CURRENT_SIGNAL

CURRENT_SIGNAL = load_persisted_signal()

@app.middleware("http")
async def observability_layer(request: Request, call_next):
    print(f"📡 [{request.method}] {request.url.path}")
    try:
        return await call_next(request)
    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {repr(e)}")
        return JSONResponse(status_code=500, content={"status": "error"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "market_open": is_market_open(),
        "telegram_token_set": bool(os.getenv("TELEGRAM_BOT_TOKEN"))
    }

@app.get("/signal/latest")
def latest():
    sig = get_active_signal()
    if sig is None:
        return JSONResponse(status_code=404, content={"status": "AWAITING_EXECUTION"})
    return sig

@app.post("/signal/execute")
def execute():
    global CURRENT_SIGNAL
    
    if not is_market_open():
        return JSONResponse(status_code=403, content={"status": "MARKET_CLOSED"})

    if get_active_signal():
        return JSONResponse(status_code=409, content={"status": "ALREADY_EXECUTED"})

    # Phase 1: Pure Execution
    sig = get_latest_signal_safe()
    new_signal_id = f"live-{datetime.now(timezone.utc).strftime('%Y%m%d')}-001"
    CURRENT_SIGNAL = {
        "signal_id": new_signal_id,
        "status": "EXECUTED",
        "asset": sig["asset"],
        "direction": sig["direction"],
        "entry": sig["entry"],
        "tp": sig["tp"],
        "sl": sig["sl"],
        "confidence": sig["confidence"],
        "executed_at": sig["timestamp"],
        "validity": "ACTIVE",
        "mode": "LIVE" if os.getenv("LIVE_MODE") == "true" else "SIMULATION"
    }
    
    # Save log
    save_log(CURRENT_SIGNAL)
    return CURRENT_SIGNAL

def save_log(signal):
    with open("execution_log.json", "w") as f:
        json.dump(signal, f, indent=2)

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        print(f"📥 Telegram Webhook received: {json.dumps(data)}")
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if text.startswith("/signal") and chat_id:
            print(f"🔍 Signal requested by chat_id: {chat_id}")
        if text.startswith("/signal") and chat_id:
            print(f"🔍 Signal requested by chat_id: {chat_id}")
            
            # DIRECT INTERNAL CALL (Avoid Deadlock/Timeout)
            try:
                # 1. Check if we have an executed signal in memory first (Highest priority)
                if CURRENT_SIGNAL:
                    print("✅ Found Executed Signal in memory.")
                    send_telegram(chat_id, CURRENT_SIGNAL)
                else:
                    # 2. If no executed signal, check Engine status (Market Closed / Waiting)
                    print("🔄 Checking Engine Status...")
                    engine_status = get_latest_signal_safe()
                    print(f"✅ Engine Status: {engine_status.get('status')}")
                    send_telegram(chat_id, engine_status)
                
            except Exception as err:
                print(f"❌ Internal Signal Check Failed: {err}")
                bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
                if bot_token:
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    requests.post(url, json={
                        "chat_id": chat_id, 
                        "text": f"⚠️ System Error: {str(err)}"
                    })
    except Exception as e:
        print(f"🔥 Webhook error: {repr(e)}")
    return {"ok": True}
