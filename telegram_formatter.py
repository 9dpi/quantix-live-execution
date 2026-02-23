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
    status = signal.get("status", "ACTIVE")
    if isinstance(status, str):
        status = status.upper()
    
    # 1. SPECIAL STATUS: MARKET CLOSED
    if status == "MARKET_CLOSED":
        return (
            "⚡️ SIGNAL GENIUS AI\n\n"
            "Status: Market Closed 🌑\n\n"
            "The Forex market is currently closed.\n"
            "No signals generated on weekends.\n\n"
            "System will auto-resume on Monday."
        )

    # 2. SPECIAL STATUS: WAITING
    if status in ["AWAITING_EXECUTION", "WAITING"]:
        return (
            "⚡️ SIGNAL GENIUS AI\n\n"
            "Status: Monitoring Market... ⏳\n\n"
            "System is scanning for high-probability setups.\n"
            "No trade decision executed yet.\n\n"
            "Please wait for the next snapshot."
        )

    # Standard Fields Extraction
    asset = signal.get("asset") or signal.get("symbol") or "EURUSD"
    asset = asset.replace("/", "")
    timeframe = signal.get("timeframe", "M15")
    direction = str(signal.get("direction", "N/A")).upper()
    dir_emoji = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
    
    confidence = signal.get("confidence") or signal.get("ai_confidence") or 0
    if isinstance(confidence, float) and confidence <= 1.0:
        confidence = int(confidence * 100)
    
    strength = signal.get("strength") or 0
    if isinstance(strength, (int, float)) and strength <= 1.0:
        strength_pct = f"{int(strength * 100)}%"
    else:
        strength_pct = str(strength)

    entry = signal.get("entry") or signal.get("entry_low") or "N/A"
    tp = signal.get("tp") or "N/A"
    sl = signal.get("sl") or "N/A"

    # 3. SPECIAL STATUS: HITS
    if status in ["TP_HIT", "CLOSED_TP", "TP HIT"]:
        return (
            f"🎯 *TAKE PROFIT HIT*\n\n"
            f"{asset} | {direction} {dir_emoji}\n"
            f"Target: {tp}\n\n"
            f"💰 Result: 🟢 PROFIT\n"
            f"Signal ID: {signal.get('id', 'N/A')}"
        )

    if status in ["SL_HIT", "CLOSED_SL", "SL HIT"]:
        return (
            f"🛑 *STOP LOSS HIT*\n\n"
            f"{asset} | {direction} {dir_emoji}\n"
            f"Exit: {sl}\n\n"
            f"📉 Result: 🔴 DEFEAT\n"
            f"Signal ID: {signal.get('id', 'N/A')}"
        )

    if status in ["ENTRY_HIT", "ENTRY HIT"]:
        return (
            f"🚀 *SIGNAL ACTIVATED*\n\n"
            f"{asset} | {direction} {dir_emoji}\n"
            f"Entry: {entry}\n\n"
            f"Status: 🔵 LIVE TRADE\n"
            f"Signal ID: {signal.get('id', 'N/A')}"
        )

    # TEMPLATE 3 – SIGNAL ULTRA (95%+ FAST ALERT)
    if confidence >= 95 and status != "EXPIRED":
        return (
            f"🚨 *ULTRA SIGNAL (95%+)*\n\n"
            f"{asset} | {timeframe}\n"
            f"{dir_emoji} {direction}\n\n"
            f"Status: 🟢 ACTIVE\n"
            f"Entry window: OPEN\n\n"
            f"Confidence: {confidence}%\n"
            f"Strength: {strength_pct}\n\n"
            f"🎯 Entry: {entry}\n"
            f"💰 TP: {tp}\n"
            f"🛑 SL: {sl}\n"
        )

    # TEMPLATE 2 – SIGNAL ĐÃ HẾT ENTRY (EXPIRED – RECORD)
    if status in ["EXPIRED", "CLOSED"]:
        result = signal.get("result", "N/A")
        if result == "N/A": result = "Closed"
        return (
            f"⚡️ *SIGNAL GENIUS AI*\n\n"
            f"Asset: {asset}\n"
            f"Timeframe: {timeframe}\n"
            f"Direction: {dir_emoji} {direction}\n\n"
            f"Status: ⛔ EXPIRED (for record only)\n\n"
            f"Entry: {entry}\n"
            f"TP: {tp}\n"
            f"SL: {sl}\n\n"
            f"Result: {result}"
        )

    # TEMPLATE 1 – SIGNAL CÒN HIỆU LỰC (ACTIVE)
    validity_min = signal.get("validity", 90)
    passed = signal.get("validity_passed", 0)
    remaining = max(1, validity_min - passed)
    
    return (
        f"⚡️ *SIGNAL GENIUS AI*\n\n"
        f"Asset: {asset}\n"
        f"Timeframe: {timeframe}\n"
        f"Direction: {dir_emoji} {direction}\n\n"
        f"Status: 🟢 ACTIVE\n"
        f"Valid for: ~{remaining} minutes\n\n"
        f"Confidence: {confidence}%\n"
        f"Force/Strength: {strength_pct}\n\n"
        f"🎯 Entry: {entry}\n"
        f"💰 TP: {tp}\n"
        f"🛑 SL: {sl}\n"
    )

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
            "parse_mode": "Markdown",
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
