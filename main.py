from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from signal_engine import get_latest_signal_safe, is_market_open
from telegram_formatter import send_telegram, format_signal_message
import os
import json
import requests
from datetime import datetime, timezone

EXECUTION_LOG_API = "https://raw.githubusercontent.com/9dpi/quantix-live-execution/main/auto_execution_log.jsonl"

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

@app.get("/data-feed/health")
def data_feed_health():
    """
    Data feed health status endpoint
    Shows if external market data is available
    """
    try:
        if os.path.exists("data_feed_health.json"):
            with open("data_feed_health.json", "r") as f:
                health_data = json.load(f)
                return health_data
        else:
            return {
                "status": "unknown",
                "reason": "No health check performed yet"
            }
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }

@app.get("/signal/latest")
def latest():
    # 1. First priority: Signal already executed and locked in this session
    sig = get_active_signal()
    if sig:
        return sig
    
    # 2. Second priority: Check for valid ACTIVE signal in Database (Pre-execution)
    # This ensures "Real Data" is shown as soon as the Miner pushes it.
    try:
        fresh_sig = get_latest_signal_safe()
        if fresh_sig:
            # We found a real signal from the Miner
            # We return it to the frontend so the user sees "ACTIVE"
            # The frontend 'validity' logic will handle if it's expired
            return fresh_sig
    except Exception as e:
        print(f"⚠️ Failed to fetch fresh signal: {e}")

    return JSONResponse(status_code=404, content={"status": "AWAITING_EXECUTION"})

@app.post("/signal/execute")
def execute():
    global CURRENT_SIGNAL
    
    if not is_market_open():
        return JSONResponse(status_code=403, content={"status": "MARKET_CLOSED"})

    if get_active_signal():
        return JSONResponse(status_code=409, content={"status": "ALREADY_EXECUTED"})

    # Phase 1: Pure Execution
    sig = get_latest_signal_safe()
    if not sig:
        return JSONResponse(status_code=404, content={"status": "NO_ACTIVE_SIGNAL", "message": "No active signals found in AI Core [T1]"})

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
            
            try:
                # 1. 1st Choice: Live signal in memory
                if CURRENT_SIGNAL:
                    print("✅ Found Live Signal in memory.")
                    send_telegram(chat_id, CURRENT_SIGNAL)
                else:
                    # 2. 2nd Choice: Check GitHub Logs (What the Web shows)
                    print("🔄 Checking GitHub Logs for 1:1 mapping...")
                    try:
                        log_response = requests.get(EXECUTION_LOG_API, timeout=5)
                        if log_response.ok:
                            lines = log_response.text.strip().split('\n')
                            if lines:
                                latest_log = json.loads(lines[-1])
                                # Add status for formatter
                                latest_log["status"] = "SIGNAL RECORD (Web Sync)"
                                send_telegram(chat_id, latest_log)
                                return {"ok": True}
                    except Exception as log_err:
                        print(f"⚠️ GitHub Log fetch failed: {log_err}")

                    # 3. 3rd Choice: Engine status (Waiting)
                    print("🔄 Engine is currently waiting...")
                    waiting_status = {
                        "status": "AWAITING_EXECUTION",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    send_telegram(chat_id, waiting_status)
                
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
