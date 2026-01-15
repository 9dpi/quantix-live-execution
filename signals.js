/**
 * Signals Formatter - Trader-grade Logic (Rule-Based Engine Sync)
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

  return `
  <div class="signal-card">
    <div class="signal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <h2 style="margin: 0; font-size: 20px;">${p.symbol} — ${p.direction}</h2>
      <span style="font-size: 10px; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">${p.market.toUpperCase()}</span>
    </div>

    <div class="confidence" style="color:${meta.color}; font-weight: 600; margin-bottom: 8px;">
      ${meta.icon} ${p.confidence}% — ${meta.label}
    </div>

    ${meta.warning ? `<div class="warning">⚠️ ${meta.warning}</div>` : ""}

    <hr style="opacity: 0.1; margin: 16px 0;"/>

    <div class="signal-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
      <div class="detail-item">
        <b style="color: #6b7280; font-size: 10px; text-transform: uppercase;">Entry</b>
        <div style="font-size: 16px; font-weight: 600;">${p.entry}</div>
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
        🌍 <b>Session:</b> ${p.session}
    </div>

    <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
      <small style="color: #6b7280;">⏳ Expires: ${expiryTime}</small>
      <small style="color: #00d4ff; font-weight: bold; font-size: 9px;">QUANTIX CORE</small>
    </div>
  </div>
  `;
}

export function renderTelegramMessage(data) {
  if (!data || data.status !== "ok" || !data.payload) return "⚠️ No data.";
  const p = data.payload;
  const meta = getConfidenceMeta(p.confidence);

  return `
🚀 *${p.symbol} - ${p.direction}*
${meta.icon} Confidence: ${p.confidence}% (${meta.label})

${meta.warning ? `⚠️ _${meta.warning}_\n` : ""}
🎯 *Entry:* ${p.entry}
💰 *TP:* ${p.tp}
🛑 *SL:* ${p.sl}

📊 *TF:* ${p.timeframe}
🔍 *Strategy:* ${p.strategy}
🌍 *Session:* ${p.session}
⏳ *Expires:* ${new Date(p.expires_at).toUTCString()}

⚠️ _Not financial advice_
`.trim();
}
