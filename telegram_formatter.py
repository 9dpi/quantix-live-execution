import os
import requests
from datetime import datetime

def send_telegram(chat_id, signal):
    """
    Formats the signal exactly 1:1 with the Web Card layout for Telegram.
    TẮT Markdown (parse_mode) để đảm bảo bot gửi tin nhắn thành công ngay lập tức.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token or not chat_id:
        print("⚠️ Telegram credentials missing. Skipping alert.")
        return None

    ts = datetime.fromisoformat(signal["timestamp"].replace("Z", "+00:00"))
    date_str = ts.strftime("%Y-%m-%d")
    direction_emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
    
    message = (
        f"ℹ️ You are viewing today's signal\n"
        f"📅 Date: {date_str}\n"
        f"Status: Live Snapshot\n\n"
        f"📊 {signal['asset']} | M15\n"
        f"{direction_emoji} {signal['direction']} {signal['strength']}\n\n"
        f"🎯 Entry: {signal['entry']}\n"
        f"💰 TP: {signal['tp']}\n"
        f"🛑 SL: {signal['sl']}\n\n"
        f"⭐ Confidence: {signal['confidence']}%\n"
        f"🧠 Strategy: {signal['strategy']}\n"
        f"⏳ Validity: {signal.get('validity_passed', 85)} / {signal.get('validity', 90)} min\n"
        f"🌊 Volatility: {signal.get('volatility', '0.12% (Stabilized)')}\n\n"
        f"⚠️ Educational purpose only"
    )
    
    # Gửi tin nhắn dùng text thuần, KHÔNG parse_mode, kèm theo buttons
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "📈 View Chart", "url": "https://9dpi.github.io/signal-genius-ai/"},
                        {"text": "🔄 Refresh", "callback_data": "refresh_signal"}
                    ],
                    [
                        {"text": "📊 Stats", "callback_data": "view_stats"}
                    ]
                ]
            }
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print(f"✅ Telegram signal sent: {signal['asset']}")
        return r.json()
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")
        return None
