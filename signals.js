/**
 * Signals Formatter - Reusable Logic
 * Responsibility: Transform payload data to formatted output (Text or HTML)
 */

/**
 * Render signal data as Telegram message (Text)
 */
function renderTelegramMessage(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return "⚠️ No valid signal data available.";
  }

  const p = data.payload;

  const directionEmoji = p.direction === "BUY" ? "🟢 BUY" : "🔴 SELL";
  const confidenceEmoji =
    p.confidence >= 95 ? "🔥" :
      p.confidence >= 90 ? "⚡" :
        "⚠️";

  return `
${directionEmoji} ${p.asset} (${p.timeframe})

ENTRY: ${p.entry[0].toFixed(5)} – ${p.entry[1].toFixed(5)}
TP: ${p.tp.toFixed(5)}
SL: ${p.sl.toFixed(5)}

CONFIDENCE: ${p.confidence}% ${confidenceEmoji}
SESSION: ${p.session}
`.trim();
}

/**
 * Render signal data as HTML Card
 */
function renderSignalHTML(data) {
  if (!data || data.status !== "ok" || !data.payload) {
    return `
      <div class="signal-card error">
        ⚠️ No valid signal data available
      </div>
    `;
  }

  const p = data.payload;

  const directionIcon = p.direction === "BUY" ? "🟢 BUY" : "🔴 SELL";
  const cardClass = p.direction === "BUY" ? "buy" : "sell";

  const confidenceWarning =
    p.confidence < 95
      ? `<div class="warning">⚠️ Low confidence – Observation only</div>`
      : "";

  return `
    <div class="signal-card ${cardClass}">
      <div class="signal-header">
        <div class="asset">${p.asset}</div>
        <div class="direction">${directionIcon}</div>
      </div>

      <div class="signal-meta">
        ⏳ Timeframe: <b>${p.timeframe}</b><br/>
        🌍 Session: <b>${p.session.replace("-", " → ")}</b>
      </div>

      <div class="price-box">
        <div>
          <label>Entry Zone</label>
          <div class="price">
            ${p.entry[0].toFixed(5)} – ${p.entry[1].toFixed(5)}
          </div>
        </div>
        <div>
          <label>Take Profit</label>
          <div class="price tp">${p.tp.toFixed(5)}</div>
        </div>
        <div>
          <label>Stop Loss</label>
          <div class="price sl">${p.sl.toFixed(5)}</div>
        </div>
      </div>

      <div class="signal-footer">
        <div class="confidence">
          🧠 AI Confidence: <b>${p.confidence}%</b> ⭐
        </div>
        <div class="source">
          Source: Quantix AI Core
        </div>
      </div>

      ${confidenceWarning}

      <div class="disclaimer">
        ⚠️ Not financial advice. Trade responsibly.
      </div>
    </div>
  `;
}
