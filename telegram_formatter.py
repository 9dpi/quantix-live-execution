import os
import requests
from datetime import datetime, timezone

def send_telegram(chat_id, signal):
    """
    Standard Copier Format for Quantix Live Execution.
    Fixed format - DO NOT ALTER.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or not chat_id:
        return None

    # Parse time for standard display
    ts_str = signal.get('executed_at') or signal.get('timestamp')
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        time_formatted = ts.strftime("%Y-%m-%d %H:%M UTC")
    except:
        time_formatted = ts_str

    # FIXED COPIER FORMAT
    msg = (
        f"#QX_SIGNAL\n"
        f"PAIR: {signal['asset'].replace('/', '')}\n"
        f"TYPE: {signal['direction']}\n"
        f"ENTRY: MARKET\n"
        f"SL: {signal['sl']}\n"
        f"TP: {signal['tp']}\n"
        f"TIMEFRAME: M15\n"
        f"SIGNAL_TIME: {time_formatted}\n"
        f"TTL: 90"
    )

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML"
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return None
