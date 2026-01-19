import os
import requests
from datetime import datetime, timezone

def _format_status_badge(status: str) -> str:
    return {
        "ACTIVE": "✅ ACTIVE",
        "EXECUTED": "⚙️ EXECUTED",
        "EXPIRED": "⛔ EXPIRED",
        "SNAPSHOT": "📸 SNAPSHOT",
    }.get(status, status)

def _format_market_context(signal: dict) -> str:
    if signal.get("market_closed"):
        return (
            "📅 Market Closed (Weekend)\n"
            "This signal is a forward prediction\n"
            "Execution planned for next session\n"
        )
    return ""

def _format_execution_block(signal: dict) -> str:
    if signal.get("status") != "EXECUTED":
        return ""

    exec_data = signal.get("execution", {})
    return (
        "\n⚙️ Execution:\n"
        f"• Broker: {exec_data.get('broker', 'N/A')}\n"
        f"• Executed Price: {exec_data.get('price', 'N/A')}\n"
        f"• Time: {exec_data.get('time', 'N/A')}\n"
    )

def format_signal_message(signal: dict) -> str:
    symbol = signal.get("asset") or signal.get("symbol") or "N/A"
    timeframe = signal.get("timeframe", "M15")
    direction = signal.get("direction", "N/A")
    status = signal.get("status", "EXECUTED")
    validity = signal.get("validity", "ACTIVE")
    
    entry = signal.get("entry", "N/A")
    tp = signal.get("tp", "N/A")
    sl = signal.get("sl", "N/A")

    message = (
        "Signal Genius AI\n"
        f"Status: {status}\n"
        f"Validity: {validity}\n\n"
        f"{symbol} | {timeframe}\n"
        f"{'🟢 BUY' if direction == 'BUY' else '🔴 SELL'}\n\n"
        f"🎯 Entry: {entry}\n"
        f"💰 TP: {tp}\n"
        f"🛑 SL: {sl}\n\n"
        "⚠️ Educational purpose only"
    )
    return message

def send_telegram(chat_id, signal):
    """
    Sends the formatted signal message to Telegram with interactive buttons.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or not chat_id:
        return None

    message = format_signal_message(signal)

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "📈 View Dashboard", "url": "https://www.signalgeniusai.com/"},
                        {"text": "🔄 Refresh", "url": "https://www.signalgeniusai.com/"}
                    ]
                ]
            }
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return None
