/**
 * Signals Formatter - Trader-grade Logic
 * Responsibility: Transform payload data to professional Text or HTML output
 */

/**
 * Get visual meta based on confidence level
 * @param {number} confidence 
 */
export function getConfidenceMeta(confidence) {
  if (confidence >= 90) {
    return {
      label: "HIGH CONFIDENCE",
      color: "#16a34a",
      icon: "🟢",
      warning: null
    }
  }

  if (confidence >= 80) {
    return {
      label: "MEDIUM CONFIDENCE",
      color: "#f59e0b",
      icon: "🟡",
      warning: "Trade with caution. Wait for confirmation."
    }
  }

  return {
    label: "LOW CONFIDENCE",
    color: "#dc2626",
    icon: "🔴",
    warning: "Low probability setup. For reference only."
  }
}

/**
 * Render signal data as HTML Card
 * @param {Object} data - API Response
 */
export function renderCard(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return `<div class="signal-card error">⚠️ No valid signal data available</div>`;
  }

  const p = data.payload;
  const meta = getConfidenceMeta(p.confidence);

  return `
  <div class="signal-card">
    <div class="signal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <h2 style="margin: 0; font-size: 20px;">${p.asset} — ${p.direction}</h2>
    </div>

    <div class="confidence"
         style="color:${meta.color}; font-weight: 600; margin-bottom: 8px;">
      ${meta.icon} ${p.confidence}% — ${meta.label}
    </div>

    ${meta.warning ? `
      <div class="warning">
        ⚠️ ${meta.warning}
      </div>` : ""}

    <hr style="opacity: 0.1; margin: 16px 0;"/>

    <div class="signal-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
      <p style="margin: 4px 0;"><b>Entry:</b><br/> ${p.entry[0]} – ${p.entry[1]}</p>
      <p style="margin: 4px 0;"><b>TF:</b><br/> ${p.timeframe}</p>
      <p style="margin: 4px 0;"><b>TP:</b><br/> <span style="color: #16a34a">${p.tp}</span></p>
      <p style="margin: 4px 0;"><b>SL:</b><br/> <span style="color: #dc2626">${p.sl}</span></p>
    </div>

    <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
      <small style="color: #6b7280;">
        Expires: ${new Date(p.expires_at).toLocaleTimeString()}
      </small>
      <small style="color: #6b7280; font-size: 10px;">
        Quantix AI Core
      </small>
    </div>
  </div>
  `;
}

/**
 * Render signal data as Telegram message (Text)
 * @param {Object} data - API Response
 */
export function renderTelegramMessage(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return "⚠️ No valid signal data available.";
  }

  const p = data.payload;
  const meta = getConfidenceMeta(p.confidence);

  return `
${p.asset}

📌 Trade: ${p.direction}
${meta.icon} Confidence: ${p.confidence}% (${meta.label})

${meta.warning ? `⚠️ ${meta.warning}\n` : ""}
🎯 Entry: ${p.entry[0]} – ${p.entry[1]}
💰 TP: ${p.tp}
🛑 SL: ${p.sl}

⏰ TF: ${p.timeframe}
⏳ Expires: ${new Date(p.expires_at).toUTCString()}

⚠️ Not financial advice
`.trim();
}
