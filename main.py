from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from signal_engine import get_latest_signal_safe
from telegram import send_telegram
import os
import requests

app = FastAPI()

@app.middleware("http")
async def global_guard(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("🔥 GLOBAL CRASH PREVENTED:", repr(e))
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "mode": "stabilizer"}
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/signal/latest")
def latest():
    return get_latest_signal_safe()

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
