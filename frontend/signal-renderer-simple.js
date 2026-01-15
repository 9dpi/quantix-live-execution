/**
 * Signal Renderer - Simple, No Framework, Copy-Paste Ready
 * Renders JSON → Signal Card for traders
 */

/**
 * Render signal card from API data
 * @param {Object} data - API response data
 */
function renderSignalCard(data) {
    const root = document.getElementById("signal-root");
    if (!root) return;

    // Guard: Check for valid data
    if (!data || data.status !== "ok" || !data.payload) {
        root.innerHTML = `
      <div class="signal-card error">
        ⚠️ No valid signal data available
      </div>
    `;
        return;
    }

    const p = data.payload;

    const directionIcon = p.direction === "BUY" ? "🟢 BUY" : "🔴 SELL";
    const cardClass = p.direction === "BUY" ? "buy" : "sell";

    const confidenceWarning =
        p.confidence < 95
            ? `<div class="warning">⚠️ Low confidence – Observation only</div>`
            : "";

    root.innerHTML = `
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

/**
 * Fetch and render signal from API
 * @param {string} apiUrl - API endpoint URL
 */
function fetchAndRenderSignal(apiUrl) {
    fetch(apiUrl)
        .then(res => res.json())
        .then(data => renderSignalCard(data))
        .catch(() => {
            renderSignalCard(null);
        });
}
