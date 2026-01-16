from datetime import datetime, timezone

def get_confidence_meta(c: int) -> dict:
    """Consolidated confidence mapping (Sync with Web)."""
    if c >= 75: return {"label": "STRONG", "emoji": "🟢"}
    if c >= 60: return {"label": "NORMAL", "emoji": "🔵"}
    if c >= 50: return {"label": "LOW", "emoji": "🟡"}
    return {"label": "NO TRADE", "emoji": "🔴"}

def calc_remaining_minutes(generated_at_iso: str, expiry_minutes: int) -> int:
    """Calculate minutes remaining for a signal."""
    try:
        now = datetime.now(timezone.utc)
        # Parse ISO string handling potential 'Z' or '+00:00'
        gen_at = datetime.fromisoformat(generated_at_iso.replace('Z', '+00:00'))
        elapsed = (now - gen_at).total_seconds() / 60
        remaining = int(expiry_minutes - elapsed)
        return max(0, remaining)
    except Exception:
        return 0

def render_telegram_message(signal_data: dict) -> str:
    """
    Format signal data for Telegram using HTML (Sync with Web).
    """
    symbol = signal_data.get('symbol') or signal_data.get('asset', 'EUR/USD')
    timeframe = signal_data.get('timeframe', 'M15')
    direction = signal_data.get('direction', 'BUY')
    # Entry can be a list [1.23] or a number
    entry_val = signal_data.get('entry', [0])[0] if isinstance(signal_data.get('entry'), list) else signal_data.get('entry', 0)
    tp = signal_data.get('tp', 0)
    sl = signal_data.get('sl', 0)
    confidence = signal_data.get('confidence', 0)
    strategy = signal_data.get('strategy', 'Rule Engine')
    gen_at = signal_data.get('generated_at', datetime.now(timezone.utc).isoformat())
    expiry_mins = signal_data.get('expiry', {}).get('minutes', 45)
    
    conf = get_confidence_meta(confidence)
    remaining = calc_remaining_minutes(gen_at, expiry_mins)
    
    message = f"""<b>📊 {symbol} | {timeframe}</b>
{conf['emoji']} <b>{direction}</b> ({conf['label']})

🎯 <b>Entry:</b> {entry_val}
💰 <b>TP:</b> {tp}
🛑 <b>SL:</b> {sl}

⭐ <b>Confidence:</b> {confidence}%
🧠 <b>Strategy:</b> {strategy}
⏳ <b>Validity:</b> {remaining} / {expiry_mins} min"""

    # Add Volatility Info if available
    vol = signal_data.get('volatility')
    if vol:
        atr_pct = vol.get('atr_percent', 0)
        state = vol.get('state', 'normal').capitalize()
        message += f"\n📉 <b>Volatility:</b> {atr_pct}% ({state})"

    message += f"\n\n⚠️ <i>Educational purpose only</i>"
    
    return message.strip()

def render_telegram_payload(signal_data: dict) -> dict:
    """Generate Telegram payload with interactive buttons."""
    symbol = signal_data.get('symbol') or signal_data.get('asset', 'EUR/USD')
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
