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
    status = signal.get("status", "EXECUTED")
    
    # 1. SPECIAL STATUS: MARKET CLOSED
    if status == "MARKET_CLOSED":
        return (
            "SIGNAL GENIUS AI\n"
            "Status: Market Closed 🌑\n\n"
            "The Forex market is currently closed.\n"
            "No signals generated on weekends.\n\n"
            "System will auto-resume on Monday."
        )

    # 2. SPECIAL STATUS: WAITING
    if status in ["AWAITING_EXECUTION", "WAITING"]:
        return (
            "SIGNAL GENIUS AI\n"
            "Status: Monitoring Market... ⏳\n\n"
            "System is scanning for high-probability setups.\n"
            "No trade decision executed yet.\n\n"
            "Please wait for the next snapshot."
        )

    # 3. STANDARD SIGNAL FORMAT
    symbol = signal.get("asset") or signal.get("symbol") or "EUR/USD"
    timeframe = signal.get("timeframe", "M15")
    direction = signal.get("direction", "N/A")
    validity = signal.get("validity_status") or signal.get("validity") or "ACTIVE"
    
    entry = signal.get("entry", "N/A")
    tp = signal.get("tp", "N/A")
    sl = signal.get("sl", "N/A")
    
    # Emoji
    dir_emoji = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"

    message = (
        "SIGNAL GENIUS AI\n"
        f"Status: {status}\n"
        f"Validity: {validity}\n\n"
        f"{symbol} | {timeframe}\n"
        f"{dir_emoji} {direction}\n\n"
        f"🎯 Entry: {entry}\n"
        f"💰 TP: {tp}\n"
        f"🛑 SL: {sl}\n\n"
        f"--\n"
        f"⚠️ Educational purpose only\n"
        f"--"
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
                        {"text": "📈 View Latest Signal", "url": "https://www.signalgeniusai.com/"}
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
