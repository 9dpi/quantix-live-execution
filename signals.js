/**
 * Signals Formatter - Trader-grade Logic
 * Shared formatter for Web and Telegram
 */

export function getConfidenceMeta(confidence) {
  if (confidence >= 75) {
    return {
      label: "STRONG",
      class: "confidence-75",
      color: "#16a34a",
      icon: "🟢",
      warning: null
    }
  }
  if (confidence >= 60) {
    return {
      label: "NORMAL",
      class: "confidence-60",
      color: "#2563eb",
      icon: "🔵",
      warning: "Trade with caution. Wait for confirmation."
    }
  }
  if (confidence >= 50) {
    return {
      label: "LOW",
      class: "confidence-50",
      color: "#ca8a04",
      icon: "🟡",
      warning: "Low probability setup. For reference only."
    }
  }
  return {
    label: "NO TRADE",
    class: "confidence-low",
    color: "#dc2626",
    icon: "�",
    warning: "Risky market conditions. No trade recommended."
  }
}

export function calcExpiryPercent(createdAt, expiryMinutes) {
  if (!createdAt || !expiryMinutes) return 0;
  const now = Date.now();
  const start = new Date(createdAt).getTime();
  const elapsed = (now - start) / 60000; // minutes
  return Math.min(100, Math.max(0, (elapsed / expiryMinutes) * 100));
}

export function renderCard(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return `<div class="signal-card error">⚠️ No valid signal data available</div>`;
  }

  const p = data.payload;
  const meta = getConfidenceMeta(p.confidence);

  // Expiry calculation
  const expiryMinutes = p.expiry?.minutes || 30;
  const expiryPercent = calcExpiryPercent(p.generated_at, expiryMinutes);
  const timeLeft = Math.max(0, Math.round(expiryMinutes * (1 - expiryPercent / 100)));

  // Handle entry as single value or array
  const entryDisplay = Array.isArray(p.entry)
    ? `${p.entry[0]}`
    : p.entry;

  return `
  <div class="signal-card">
    <div class="signal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
      <h2 style="margin: 0; font-size: 18px; color: #9ca3af; font-weight: 500;">${p.symbol || p.asset}</h2>
      <span style="font-size: 9px; background: rgba(255,255,255,0.05); color: #6b7280; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.05);">${p.mode || 'NORMAL'}</span>
    </div>

    <div style="font-size: 28px; font-weight: 800; color: ${p.direction === 'BUY' ? '#22c55e' : '#ef4444'}; margin-bottom: 16px;">
      ${p.direction === 'BUY' ? '🟢 BUY' : '🔴 SELL'}
    </div>

    <div class="confidence-badge ${meta.class}">
      ${meta.icon} ${p.confidence}% ${meta.label}
    </div>

    ${p.meta?.status === 'replay' ? `
      <div class="badge-replay">
        🔁 Today's Signal (Replay)
      </div>
    ` : ''}

    ${meta.warning ? `<div class="warning" style="margin-top: 0; margin-bottom: 16px;">${meta.warning}</div>` : ""}

    <div class="signal-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; background: rgba(255,255,255,0.02); padding: 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
      <div class="detail-item">
        <b>Entry</b>
        <div style="font-size: 18px; font-weight: 700; color: #fff;">${entryDisplay}</div>
      </div>
      <div class="detail-item">
        <b>Timeline</b>
        <div style="font-size: 18px; font-weight: 700; color: #fff;">${p.timeframe}</div>
      </div>
      <div class="detail-item">
        <b>Take Profit</b>
        <div style="font-size: 18px; font-weight: 700; color: #22c55e;">${p.tp}</div>
      </div>
      <div class="detail-item">
        <b>Stop Loss</b>
        <div style="font-size: 18px; font-weight: 700; color: #ef4444;">${p.sl}</div>
      </div>
    </div>

    <div class="expiry-container">
      <div class="expiry-label">
        <span>⏳ Signal Validity</span>
        <span>${timeLeft} / ${expiryMinutes} min</span>
      </div>
      <div class="expiry-bar">
        <div class="expiry-progress" style="width: ${100 - expiryPercent}%"></div>
      </div>
    </div>

    <div style="margin-top: 16px; padding: 12px; background: rgba(0,0,0,0.2); border-radius: 6px; font-size: 11px; color: #9ca3af; border: 1px solid rgba(255,255,255,0.03);">
        🔍 <b>Strategy:</b> ${p.strategy}<br/>
        🌍 <b>Session:</b> ${p.session}${p.volatility ? `<br/>📉 <b>Volatility:</b> ${p.volatility.atr_percent}% (${p.volatility.state})` : ""}
    </div>

    <div style="margin-top: 16px; text-align: center; color: #4b5563; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">
      Quantix AI Core V1.0
    </div>
  </div>
  `;
}

/**
 * Telegram Message Formatter (Legacy - keeping for internal use)
 */
export function renderTelegramMessage(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return "⚠️ *Signal unavailable*";
  }

  const p = data.payload;
  const confidence = p.confidence ?? "50";

  // Escape for Telegram Markdown v2
  const escape = (text) => String(text).replace(/[_*[\]()~`>#+\-=|{}.!]/g, "\\$&");
  const directionEmoji = p.direction === "BUY" ? "🟢 BUY" : "🔴 SELL";
  const asset = p.symbol || p.asset || "EUR/USD";

  return `
<b>📊 ${escape(asset)} | ${escape(p.timeframe)}</b>
${directionEmoji} (Confidence: <b>${confidence}%</b>)

🎯 Entry: ${escape(p.entry[0])}
🎯 TP: ${escape(p.tp)}
🛑 SL: ${escape(p.sl)}
`.trim();
}
