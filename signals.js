/**
 * Signals Formatter - Trader-grade Logic
 * Shared formatter for Web and Telegram
 */

export function getConfidenceMeta(confidence) {
  if (confidence >= 90) {
    return { label: "HIGH CONFIDENCE", color: "#16a34a", icon: "🟢", warning: null }
  }
  if (confidence >= 75) {
    return { label: "MEDIUM CONFIDENCE", color: "#f59e0b", icon: "🟡", warning: "Trade with caution. Wait for confirmation." }
  }
  return { label: "LOW CONFIDENCE", color: "#dc2626", icon: "🔴", warning: "Low probability setup. For reference only." }
}

export function renderCard(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return `<div class="signal-card error">⚠️ No valid signal data available</div>`;
  }

  const p = data.payload;
  const meta = getConfidenceMeta(p.confidence);
  const expiryTime = new Date(p.expires_at).toLocaleTimeString();

  // Handle entry as single value or array
  const entryDisplay = Array.isArray(p.entry)
    ? `${p.entry[0]} – ${p.entry[1]}`
    : p.entry;

  return `
  <div class="signal-card">
    <div class="signal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <h2 style="margin: 0; font-size: 20px;">${p.symbol || p.asset} — ${p.direction}</h2>
      <span style="font-size: 10px; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">${p.market?.toUpperCase() || 'REAL'}</span>
    </div>

    <div class="confidence" style="color:${meta.color}; font-weight: 600; margin-bottom: 8px;">
      ${meta.icon} ${p.confidence}% — ${meta.label}
    </div>

    ${meta.warning ? `<div class="warning">⚠️ ${meta.warning}</div>` : ""}

    <hr style="opacity: 0.1; margin: 16px 0;"/>

    <div class="signal-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
      <div class="detail-item">
        <b style="color: #6b7280; font-size: 10px; text-transform: uppercase;">Entry</b>
        <div style="font-size: 16px; font-weight: 600;">${entryDisplay}</div>
      </div>
      <div class="detail-item">
        <b style="color: #6b7280; font-size: 10px; text-transform: uppercase;">Timeframe</b>
        <div style="font-size: 16px; font-weight: 600;">${p.timeframe}</div>
      </div>
      <div class="detail-item">
        <b style="color: #6b7280; font-size: 10px; text-transform: uppercase;">Take Profit</b>
        <div style="font-size: 16px; font-weight: 600; color: #16a34a;">${p.tp}</div>
      </div>
      <div class="detail-item">
        <b style="color: #6b7280; font-size: 10px; text-transform: uppercase;">Stop Loss</b>
        <div style="font-size: 16px; font-weight: 600; color: #ef4444;">${p.sl}</div>
      </div>
    </div>

    <div style="margin-top: 16px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; font-size: 11px; color: #9ca3af;">
        🔍 <b>Strategy:</b> ${p.strategy}<br/>
        🌍 <b>Session:</b> ${p.session}${p.volatility ? `<br/>📉 <b>Volatility:</b> ${p.volatility.atr_percent}% (${p.volatility.state})` : ""}
    </div>

    ${p.confidence_meta?.telegram ? `
      <div style="margin-top: 16px; padding: 12px; background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 102, 255, 0.05)); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; text-align: center;">
        <div style="font-size: 12px; color: #00d4ff; margin-bottom: 6px;">⭐ <b>Premium Signal</b></div>
        <div style="font-size: 10px; color: #9ca3af;">High-confidence signals like this are delivered instantly via Telegram</div>
      </div>
    ` : `
      <div style="margin-top: 16px; padding: 10px; background: rgba(255, 136, 0, 0.05); border-left: 3px solid rgba(255, 136, 0, 0.5); border-radius: 4px;">
        <div style="font-size: 10px; color: #9ca3af;">
          ⚠️ This signal is for reference only. Premium signals (≥85% confidence) are sent to Telegram subscribers.
        </div>
      </div>
    `}

    <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
      <small style="color: #6b7280;">⏳ Expires: ${expiryTime}</small>
      <small style="color: #00d4ff; font-weight: bold; font-size: 9px;">QUANTIX CORE</small>
    </div>
  </div>
  `;
}

/**
 * Telegram Message Formatter (Markdown v2 Safe)
 * Reusable for Telegram Bot - No DOM dependencies
 */
export function renderTelegramMessage(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return "⚠️ *Signal unavailable*";
  }

  const p = data.payload;
  const confidence = p.confidence ?? "N/A";
  const riskLabel =
    confidence >= 80 ? "Low" :
      confidence >= 60 ? "Medium" : "High";

  // Escape for Telegram Markdown v2
  const escape = (text) =>
    String(text).replace(/[_*[\]()~`>#+\-=|{}.!]/g, "\\$&");

  // Handle entry as array or single value
  const entryText = Array.isArray(p.entry)
    ? `${escape(p.entry[0])} – ${escape(p.entry[1])}`
    : escape(p.entry);

  const directionEmoji = p.direction === "BUY" ? "🟢 BUY" : "� SELL";
  const asset = p.symbol || p.asset || "EUR/USD";

  return `
📊 *${escape(asset)}* \\| *${escape(p.timeframe)}*
${directionEmoji} \\(Confidence: *${confidence}%*\\)

� *Entry:* ${entryText}
🎯 *TP:* ${escape(p.tp)}
🛑 *SL:* ${escape(p.sl)}

🕒 *Session:* ${escape(p.session)}
⚠️ *Risk:* ${riskLabel}
🤖 _Signal by Quantix AI_
`.trim();
}
