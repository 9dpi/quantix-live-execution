import os
import requests
from datetime import datetime

def send_system_upgrade_notification():
    """
    Sends a specialized 'System Upgrade' notification in the standardized format.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("⚠️ Telegram credentials missing. This test requires environment variables.")
        return

    message = (
        "🚀 SYSTEM UPGRADE COMPLETED\n"
        f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        "Status: Stable & Operational\n\n"
        "🛠 Version: 1.1.0\n"
        "✨ Enhancements: \n"
        "- 1:1 Web-Telegram Sync\n"
        "- Plain-text safe mode enabled\n"
        "- UI layout optimized for mobile\n\n"
        "💡 All systems are currently green.\n"
        "⚠️ Educational purpose only"
    )
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        r = requests.post(url, json=payload, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        r.raise_for_status()
        print("✅ System Upgrade notification sent!")
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

if __name__ == "__main__":
    send_system_upgrade_notification()
