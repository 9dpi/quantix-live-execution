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
    symbol = signal.get("asset") or signal.get("symbol")
    timeframe = signal.get("timeframe", "M15")
    direction = signal["direction"]

    status = signal.get("status", "SNAPSHOT")
    validity = signal.get("validity", "")

    status_badge = _format_status_badge(status)

    entry = signal["entry"]
    tp = signal["tp"]
    sl = signal["sl"]

    confidence = signal.get("confidence")
    strategy = signal.get("strategy")
    volatility = signal.get("volatility")

    header = (
        "🧠 Quantix Live Execution\n"
        f"Status: {status_badge}\n"
    )

    if validity:
        header += f"Validity: {validity}\n"

    header += "\n"

    market_context = _format_market_context(signal)

    message = (
        header
        + market_context
        + f"📊 {symbol} | {timeframe}\n"
        f"{'🟢 BUY' if direction == 'BUY' else '🔴 SELL'}\n\n"
        f"🎯 Entry: {entry}\n"
        f"💰 TP: {tp}\n"
        f"🛑 SL: {sl}\n"
    )

    if confidence is not None:
        message += f"\n⭐ Confidence: {confidence}%"

    if strategy:
        message += f"\n🧠 Strategy: {strategy}"

    if volatility:
        message += f"\n🌊 Volatility: {volatility}"

    message += _format_execution_block(signal)

    message += "\n\n⚠️ Educational purpose only"

    return message

def send_telegram(chat_id, signal):
    """
    Sends the formatted signal message to Telegram.
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
            "parse_mode": "HTML"
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return None
