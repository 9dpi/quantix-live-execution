import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
try:
    from external_client import fetch_candles
    from signal_engine import generate_signal, generate_stabilizer_signal
    from signal_ledger import append_signal, calculate_stats, get_all_signals
    from telegram_formatter import render_telegram_message, render_telegram_payload
    from rate_limit import get_cached_daily_signal, save_daily_signal, should_push_telegram
except ImportError:
    from backend.external_client import fetch_candles
    from backend.signal_engine import generate_signal, generate_stabilizer_signal
    from backend.signal_ledger import append_signal, calculate_stats, get_all_signals
    from backend.telegram_formatter import render_telegram_message, render_telegram_payload
    from backend.rate_limit import get_cached_daily_signal, save_daily_signal, should_push_telegram

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
async def latest_signal(symbol: str = "EUR/USD", timeframe: str = "M15"):
    try:
        # 1. Check Daily Cache
        cached = get_cached_daily_signal(symbol, timeframe)
        if cached:
            # Mark as replay
            if "meta" not in cached: cached["meta"] = {}
            cached["meta"]["status"] = "replay"
            return {"status": "ok", "payload": cached}

        # 2. Try Real Fetch (Fresh)
        candles = await fetch_candles(symbol=symbol)
        signal = generate_signal(candles, timeframe=timeframe)
        
        # Mark as fresh
        if "meta" not in signal: signal["meta"] = {}
        signal["meta"]["status"] = "fresh"
        
        # 3. Save to Cache
        save_daily_signal(symbol, timeframe, signal)
        
        # 4. Log to immutable ledger
        append_signal(signal)
        
        return {
            "status": "ok",
            "payload": signal
        }
        
    except Exception as e:
        print(f"⚠️ Error fetching/generating signal: {e}")
        
        # EMERGENCY FALLBACK
        fallback_price = 1.0850 
        fallback_signal = generate_stabilizer_signal(
            fallback_price, 
            timeframe=timeframe,
            reason="Emergency Fallback"
        )
        
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

def send_telegram_message(chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict = None):
    """
    Send message to Telegram chat.
    
    Args:
        chat_id: Telegram chat ID
        text: Message text
        parse_mode: HTML (default) or Markdown
        reply_markup: Optional inline keyboard or other markup
        
    Returns:
        bool: True if sent successfully
    """
    # Validate inputs
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return False
    
    if not chat_id:
        print("❌ Invalid chat_id")
        return False
    
    if not text or not str(text).strip():
        print("❌ Empty message text")
        return False
    
    # Ensure text is string and limit length
    text = str(text).strip()[:4000]
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        print(f"📤 Sending to chat_id={chat_id}, length={len(text)}, mode={parse_mode}")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Message sent successfully")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text if e.response else 'No response'}")
        return False
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram Bot Webhook Handler
    """
    try:
        update = await request.json()
        print(f"📥 Telegram Update: {update}")
        
        # 1. Handle Callback Queries (Buttons)
        if "callback_query" in update:
            cb = update["callback_query"]
            chat_id = cb["message"]["chat"]["id"]
            cb_id = cb["id"]
            data = cb["data"]
            
            # Answer callback immediately to stop loading spinner
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", 
                         json={"callback_query_id": cb_id})
            
            if data == "refresh_signal":
                try:
                    # Respect daily policy
                    signal = get_cached_daily_signal("EUR/USD", "M15")
                    status_text = ""
                    
                    if not signal:
                        candles = await fetch_candles()
                        signal = generate_signal(candles)
                        if "meta" not in signal: signal["meta"] = {}
                        signal["meta"]["status"] = "fresh"
                        save_daily_signal("EUR/USD", "M15", signal)
                        append_signal(signal)
                    else:
                        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                        status_text = f"<b>ℹ️ Today's signal replayed</b>\n📅 Date: {today}\nStatus: Replay\n\n"
                    
                    payload = render_telegram_payload(signal)
                    final_text = status_text + payload["text"]
                    send_telegram_message(chat_id, final_text, reply_markup=payload["reply_markup"])
                except Exception as e:
                    send_telegram_message(chat_id, f"⚠️ Refresh failed: {str(e)[:50]}")
            
            elif data == "stats":
                try:
                    stats = calculate_stats()
                    msg = f"<b>📊 Performance Statistics</b>\n\nTotal Signals: {stats['total_signals']}\nWin Rate: {stats.get('win_rate', 0)}%"
                    send_telegram_message(chat_id, msg)
                except Exception:
                    send_telegram_message(chat_id, "⚠️ Stats unavailable")
            
            return {"ok": True}

        # 2. Handle Messages
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
                    "<b>🤖 Signal Genius AI</b>\n\n"
                    "Bot đã hoạt động!\n\n"
                    "<b>Commands:</b>\n"
                    "/signal - Get latest signal\n"
                    "/stats - View performance\n"
                    "/help - Show this message"
                )
            except Exception as e:
                print(f"❌ /start error: {e}")
                send_telegram_message(chat_id, "⚠️ Error processing command")
        
        elif text == "/signal":
            try:
                # Check Daily Cache
                signal = get_cached_daily_signal("EUR/USD", "M15")
                status_text = ""
                
                if not signal:
                    candles = await fetch_candles()
                    signal = generate_signal(candles)
                    if "meta" not in signal: signal["meta"] = {}
                    signal["meta"]["status"] = "fresh"
                    save_daily_signal("EUR/USD", "M15", signal)
                    append_signal(signal)
                else:
                    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                    status_text = f"<b>ℹ️ You are viewing today's signal</b>\n📅 Date: {today}\nStatus: Replay\n\n"
                
                # Use interactive payload
                payload = render_telegram_payload(signal)
                final_text = status_text + payload["text"]
                send_telegram_message(chat_id, final_text, reply_markup=payload["reply_markup"])
                
            except Exception as e:
                print(f"❌ /signal error: {e}")
                send_telegram_message(
                    chat_id,
                    f"⚠️ Signal temporarily unavailable\nReason: {str(e)[:100]}"
                )
        
        elif text == "/stats":
            try:
                stats = calculate_stats()
                msg = f"""<b>📊 Performance Statistics</b>

Total Signals: {stats['total_signals']}
Win Rate: {stats.get('win_rate', 0)}%
Avg Confidence: {stats['avg_confidence']}%

<b>By Tier:</b>
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
                    "<b>🤖 Signal Genius AI Bot</b>\n\n"
                    "<b>Commands:</b>\n"
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
        return {"ok": True, "error": "Internal error"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
