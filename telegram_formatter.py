import os
import requests

def send_telegram(chat_id, signal):
    """
    Minimalist, machine-readable Telegram formatter for Quantix Live Execution.
    Focuses on raw data and speed.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or not chat_id:
        return None

    # Format machine-readable block
    msg = (
        f"🚀 QUANTIX_EXECUTION_REPORT\n"
        f"ID: {signal.get('signal_id', 'N/A')}\n"
        f"ASSET: {signal['asset']}\n"
        f"DIR: {signal['direction']}\n"
        f"ENTRY: {signal['entry']}\n"
        f"TP: {signal['tp']}\n"
        f"SL: {signal['sl']}\n"
        f"CONF: {signal['confidence']}%\n"
        f"MODE: {signal.get('mode', 'LIVE')}\n"
        f"TIME: {signal.get('executed_at') or signal.get('timestamp')}\n"
        f"---"
    )

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"<code>{msg}</code>",
            "parse_mode": "HTML"
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return None
