import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
try:
    from external_client import fetch_candles
    from signal_engine import generate_signal, generate_stabilizer_signal
    from signal_ledger import append_signal, calculate_stats, get_all_signals
except ImportError:
    from backend.external_client import fetch_candles
    from backend.signal_engine import generate_signal, generate_stabilizer_signal
    from backend.signal_ledger import append_signal, calculate_stats, get_all_signals

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
        # 1. Try Real Fetch
        candles = await fetch_candles()
        signal = generate_signal(candles)
        
        # 2. Log to immutable ledger
        append_signal(signal)
        
        return {
            "status": "ok",
            "payload": signal
        }
        
    except Exception as e:
        print(f"⚠️ Error fetching/generating signal: {e}")
        
        # 3. EMERGENCY FALLBACK
        fallback_price = 1.0850 
        fallback_signal = generate_stabilizer_signal(
            fallback_price, 
            direction="BUY", 
            reason="Emergency Fallback"
        )
        
        # Log fallback too
        append_signal(fallback_signal)
        
        return {
            "status": "ok",
            "payload": fallback_signal
        }


@app.get("/api/v1/stats")
def get_stats():
    """
    Get performance statistics.
    
    Returns:
        - Total signals
        - Average confidence
        - Breakdown by tier
    """
    stats = calculate_stats()
    return {
        "status": "ok",
        "stats": stats
    }


@app.get("/api/v1/signals/history")
def get_history(limit: int = 50):
    """
    Get signal history (most recent first).
    
    Args:
        limit: Number of signals to return (max 100)
    """
    limit = min(limit, 100)
    signals = get_all_signals(limit=limit)
    
    return {
        "status": "ok",
        "count": len(signals),
        "signals": signals
    }


# ============================================
# TELEGRAM BOT WEBHOOK
# ============================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Send message to Telegram chat"""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram Bot Webhook Handler
    
    Receives updates from Telegram and responds to commands.
    """
    try:
        update = await request.json()
        print(f"📥 Telegram Update: {update}")
        
        # Extract message
        message = update.get("message")
        if not message:
            return {"ok": True}
        
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Command handlers with error handling
        if text == "/start":
            try:
                send_telegram_message(
                    chat_id,
                    "🤖 *Signal Genius AI*\n\n"
                    "Bot đã hoạt động\\!\n\n"
                    "Commands:\n"
                    "/signal \\- Get latest signal\n"
                    "/stats \\- View performance\n"
                    "/help \\- Show this message",
                    parse_mode="MarkdownV2"
                )
            except Exception as e:
                print(f"❌ /start error: {e}")
                send_telegram_message(chat_id, "⚠️ Error processing command")
        
        elif text == "/signal":
            # Fetch latest signal
            try:
                candles = await fetch_candles()
                signal = generate_signal(candles)
                
                # Format signal message
                p = signal
                msg = f"""📊 *{p['symbol']}* \\| {p['timeframe']}
{'🟢' if p['direction'] == 'BUY' else '🔴'} *{p['direction']}*

🎯 Entry: {p['entry']}
💰 TP: {p['tp']}
🛑 SL: {p['sl']}

⭐ Confidence: {p['confidence']}%
🧠 Strategy: {p['strategy']}

⚠️ _Not financial advice_"""
                
                send_telegram_message(chat_id, msg, parse_mode="MarkdownV2")
                
            except Exception as e:
                print(f"❌ /signal error: {e}")
                send_telegram_message(
                    chat_id,
                    f"⚠️ Signal temporarily unavailable\nReason: {str(e)[:100]}"
                )
        
        elif text == "/stats":
            try:
                stats = calculate_stats()
                msg = f"""📊 *Performance Statistics*

Total Signals: {stats['total_signals']}
Avg Confidence: {stats['avg_confidence']}%

*By Tier:*
HIGH: {stats['by_tier'].get('HIGH', {}).get('count', 0)} signals
MEDIUM: {stats['by_tier'].get('MEDIUM', {}).get('count', 0)} signals
LOW: {stats['by_tier'].get('LOW', {}).get('count', 0)} signals"""
                
                send_telegram_message(chat_id, msg)
            except Exception as e:
                print(f"❌ /stats error: {e}")
                send_telegram_message(chat_id, "⚠️ Stats temporarily unavailable")
        
        elif text == "/help":
            try:
                send_telegram_message(
                    chat_id,
                    "🤖 *Signal Genius AI Bot*\n\n"
                    "*Commands:*\n"
                    "/signal - Get latest trading signal\n"
                    "/stats - View performance statistics\n"
                    "/start - Show welcome message\n\n"
                    "⚠️ Signals are for educational purposes only."
                )
            except Exception as e:
                print(f"❌ /help error: {e}")
                send_telegram_message(chat_id, "⚠️ Error processing command")
        
        else:
            try:
                send_telegram_message(
                    chat_id,
                    "❓ Unknown command. Send /help for available commands."
                )
            except Exception as e:
                print(f"❌ Unknown command error: {e}")
        
        return {"ok": True}
        
    except Exception as e:
        print(f"❌ Webhook critical error: {e}")
        # Always return ok to prevent Telegram from retrying
        return {"ok": True, "error": "Internal error"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
