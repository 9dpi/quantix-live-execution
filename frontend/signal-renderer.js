/**
 * Signal Renderer - Transform JSON to Professional UI
 * Matching GitHub Pages Bento-Grid Design
 * Supports both Web Card and Telegram Message from same data structure
 */

/**
 * Render signal data as HTML card (for web) - Bento-Grid Style
 * @param {Object} data - Signal data from API
 * @returns {string} HTML string
 */
function renderSignalCard(data) {
  // Extract data from API response
  const payload = data.payload || data;
  const asset = payload.asset || "EUR/USD";
  const direction = payload.direction || "BUY";
  const confidence = payload.confidence || 0;
  const entry = payload.entry || [0, 0];
  const tp = payload.tp || 0;
  const sl = payload.sl || 0;
  const timeframe = payload.timeframe || "M15";
  const session = payload.session || "London-NewYork";
  const source = payload.source || "unknown";

  // Determine card class based on direction
  const cardClass = direction.toUpperCase() === "BUY" ? "buy" : "sell";
  const directionIcon = direction.toUpperCase() === "BUY" ? "🟢" : "🔴";

  // Format entry zone
  const entryZone = Array.isArray(entry)
    ? `${entry[0]} – ${entry[1]}`
    : entry;

  // Format session name
  const sessionName = session.includes("London") && session.includes("NewYork")
    ? "London → New York"
    : session;

  // Calculate R:R
  const entryMid = Array.isArray(entry) ? (entry[0] + entry[1]) / 2 : entry;
  const risk = Math.abs(entryMid - sl);
  const reward = Math.abs(tp - entryMid);
  const rr = risk > 0 ? `1 : ${(reward / risk).toFixed(2)}` : "N/A";

  // Warning if low confidence
  const warning = confidence < 85
    ? `<div class="warning-box">
         <strong>⚠️ Experimental Signal</strong>
         Lower confidence (${confidence}%). For observation only.
       </div>`
    : "";

  return `
    <div class="bento-card signal-card animate-in">
      <div class="signal-header">
        <div class="asset-name">${asset}</div>
        <div class="direction-badge ${cardClass}">${directionIcon} ${direction.toUpperCase()}</div>
      </div>

      ${warning}

      <div class="signal-details">
        <div class="detail-group">
          <div class="detail-label">Entry Zone</div>
          <div class="detail-value">${entryZone}</div>
        </div>
        <div class="detail-group">
          <div class="detail-label">Take Profit</div>
          <div class="detail-value tp-color">${tp}</div>
        </div>
        <div class="detail-group">
          <div class="detail-label">Stop Loss</div>
          <div class="detail-value sl-color">${sl}</div>
        </div>
      </div>

      <div class="confidence-row">
        <div class="confidence-badge">
          <span>🧠</span> AI Confidence: ${confidence}%
        </div>
        <div class="meta-info">
          Timeframe: <b>${timeframe}</b>
        </div>
      </div>

      <div class="strategy-notes">
        <h4>🛡️ Strategy Notes</h4>
        <ul>
          <li>Session: ${sessionName}</li>
          <li>Risk/Reward: ${rr}</li>
          <li>Expire if price hits SL before Entry</li>
          <li>Suggested Risk: 0.5% – 1% per trade</li>
        </ul>
      </div>
    </div>
  `;
}

/**
 * Render signal data as Telegram message (Markdown/Text)
 * @param {Object} data - Signal data from API
 * @returns {string} Telegram message text
 */
function renderTelegramMessage(data) {
  // Extract data from API response
  const payload = data.payload || data;
  const asset = payload.asset || "EUR/USD";
  const direction = payload.direction || "BUY";
  const confidence = payload.confidence || 0;
  const entry = payload.entry || [0, 0];
  const tp = payload.tp || 0;
  const sl = payload.sl || 0;
  const timeframe = payload.timeframe || "M15";
  const session = payload.session || "London-NewYork";

  // Format entry zone
  const entryZone = Array.isArray(entry)
    ? `${entry[0]} – ${entry[1]}`
    : entry;

  // Direction icon and text
  const directionIcon = direction.toUpperCase() === "BUY" ? "🟢" : "🔴";
  const directionText = direction.toUpperCase() === "BUY"
    ? "BUY (expect price to go up)"
    : "SELL (expect price to go down)";

  // Session name
  const sessionName = session.includes("London") && session.includes("NewYork")
    ? "London → New York Overlap"
    : session;

  // Calculate pips and R:R (simplified)
  const entryMid = Array.isArray(entry) ? (entry[0] + entry[1]) / 2 : entry;
  const targetPips = Math.abs(Math.round((tp - entryMid) * 10000));
  const risk = Math.abs(entryMid - sl);
  const reward = Math.abs(tp - entryMid);
  const rr = risk > 0 ? `1 : ${(reward / risk).toFixed(2)}` : "N/A";

  // Confidence stars
  const stars = confidence >= 95 ? "⭐" : "";

  return `
Asset: ${asset}
📌 Trade: ${directionIcon} ${directionText}
⏳ Timeframe: 15-Minute (${timeframe})
🌍 Session: ${sessionName}

💰 Price Levels:
• Entry Zone: ${entryZone}
• Take Profit (TP): ${tp}
• Stop Loss (SL): ${sl}

📏 Trade Details:
• Target: +${targetPips} pips
• Risk–Reward: ${rr}
• Suggested Risk: 0.5% – 1% per trade

🕒 Trade Type: Intraday
🧠 AI Confidence: ${confidence}% ${stars}

⏳ Auto-Expiry Rules:
• Signal is valid for this session only
• Expires at New York close or if TP or SL is hit
• Do not enter if price has already moved significantly beyond the entry zone

—
⚠️ Not financial advice. Trade responsibly.
  `.trim();
}

/**
 * Display signal in the UI
 * @param {Object} data - Signal data from API
 * @param {string} elementId - Target element ID
 */
function displaySignal(data, elementId = "signal") {
  const el = document.getElementById(elementId);
  if (!el) {
    console.error(`Element #${elementId} not found`);
    return;
  }

  // Check if it's an error response
  if (data.status === "error" || data.status === "degraded") {
    el.innerHTML = `
      <div class="error-box">
        <h3>⚠️ ${data.status === "degraded" ? "Degraded Mode" : "Error"}</h3>
        <p>${data.message || "Unable to fetch signal data"}</p>
        <p><small>The system is running in fallback mode.</small></p>
      </div>
    `;
    return;
  }

  // Check if no signal available
  if (data.status === "no_signal") {
    el.innerHTML = `
      <div class="no-signal-box">
        <h3>ℹ️ No Signal Available</h3>
        <p>AI confidence is below threshold (${data.confidence || 0}% < ${data.threshold || 85}%)</p>
        <p><small>Waiting for high-confidence setup...</small></p>
      </div>
    `;
    return;
  }

  // Render signal card
  el.innerHTML = renderSignalCard(data);

  // Also log Telegram format to console for testing
  console.log("📱 Telegram Message Format:");
  console.log(renderTelegramMessage(data));
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    renderSignalCard,
    renderTelegramMessage,
    displaySignal
  };
}
