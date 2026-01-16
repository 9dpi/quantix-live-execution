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
  const entryDisplay = Array.isArray(p.entry) ? p.entry.join(' – ') : p.entry;
  const expiryPercent_for_html = calcExpiryPercent(p.generated_at, p.expiry?.minutes || 45);

  return `
  <div class="signal-card">
    <div class="signal-header">
      <h2>${p.symbol || p.asset}</h2>
      <span>${p.mode || 'NORMAL'}</span>
    </div>

    <div class="signal-direction ${p.direction === 'BUY' ? 'buy' : 'sell'}">
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

    ${meta.warning ? `<div class="warning">⚠️ ${meta.warning}</div>` : ""}

    <div class="detail-grid">
      <div class="detail-box">
        <label>Entry</label>
        <span>${entryDisplay}</span>
      </div>
      <div class="detail-box">
        <label>Timeframe</label>
        <span>${p.timeframe}</span>
      </div>
      <div class="detail-box">
        <label>Take Profit</label>
        <span class="success">${p.tp}</span>
      </div>
      <div class="detail-box">
        <label>Stop Loss</label>
        <span class="danger">${p.sl}</span>
      </div>
    </div>

    <div class="expiry-container">
      <div class="expiry-label">
        <span>Validity</span>
        <span>${p.expiry?.label || '45 min'}</span>
      </div>
      <div class="expiry-bar">
        <div class="expiry-progress" style="width: ${expiryPercent_for_html}%"></div>
      </div>
    </div>

    <div class="signal-footer">
      <div class="signal-id">
        ID: <code>${p.signal_id || 'N/A'}</code>
      </div>
      <div class="signal-volatility">
        VOL: <span>${p.volatility?.atr_percent || '0.00'}%</span>
      </div>
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
