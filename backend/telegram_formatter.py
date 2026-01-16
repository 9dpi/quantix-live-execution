
def confidence_label(c: int) -> str:
    """Map confidence score to trader-grade labels."""
    if c >= 85: return f"🟢 HIGH ({c}%)"
    if c >= 60: return f"🟡 MEDIUM ({c}%)"
    return f"🔴 LOW ({c}%)"

def expiry_by_tf(tf: str) -> str:
    """Estimated expiry window based on timeframe."""
    mapping = {
        "M1": "5 min",
        "M5": "15 min",
        "M15": "45 min",
        "M30": "1.5 hours",
        "H1": "3 hours",
        "H4": "12 hours",
        "D1": "2 days"
    }
    return mapping.get(tf, "Unknown")

def render_telegram_message(signal_data: dict) -> str:
    """
    Format signal data for Telegram using HTML.
    """
    symbol = signal_data.get('symbol') or signal_data.get('asset', 'EUR/USD')
    timeframe = signal_data.get('timeframe', 'M15')
    direction = signal_data.get('direction', 'BUY')
    entry = signal_data.get('entry', 0)
    tp = signal_data.get('tp', 0)
    sl = signal_data.get('sl', 0)
    confidence = signal_data.get('confidence', 0)
    strategy = signal_data.get('strategy', 'Rule Engine')
    
    dir_emoji = "🟢" if direction == "BUY" else "🔴"
    conf_label = confidence_label(confidence)
    expiry = expiry_by_tf(timeframe)
    
    message = f"""<b>📊 {symbol} | {timeframe}</b>
{dir_emoji} <b>{direction}</b>

🎯 <b>Entry:</b> {entry}
💰 <b>TP:</b> {tp}
🛑 <b>SL:</b> {sl}

⭐ <b>Confidence:</b> {conf_label}"""

    # Add Volatility Info if available
    vol = signal_data.get('volatility')
    if vol:
        atr_pct = vol.get('atr_percent', 0)
        state = vol.get('state', 'normal').capitalize()
        message += f"\n📉 <b>Volatility:</b> {atr_pct}% ({state})"

    message += f"""
⏳ <b>Expires:</b> {expiry}
🧠 <b>Strategy:</b> {strategy}

⚠️ <i>Educational purpose only</i>"""
    
    return message.strip()

def render_telegram_payload(signal_data: dict) -> dict:
    """
    Generate full Telegram payload including inline keyboard.
    """
    symbol = signal_data.get('symbol') or signal_data.get('asset', 'EUR/USD')
    # Use a real chart URL template (TradingView example)
    clean_symbol = symbol.replace("/", "").replace("-", "")
    chart_url = f"https://www.tradingview.com/chart/?symbol=FX:{clean_symbol}"
    
    return {
        "text": render_telegram_message(signal_data),
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "📈 View Chart", "url": chart_url},
                    {"text": "🔄 Refresh", "callback_data": "refresh_signal"}
                ],
                [
                    {"text": "📊 Stats", "callback_data": "stats"}
                ]
            ]
        }
    }

def render_telegram_message_with_id(signal_data: dict) -> str:
    """Format signal with ID for traceability."""
    signal_id = signal_data.get('signal_id', 'N/A')
    base_message = render_telegram_message(signal_data)
    return f"🆔 <code>{signal_id}</code>\n\n{base_message}".strip()
