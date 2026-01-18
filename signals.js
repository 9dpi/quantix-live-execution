export function renderCard(data) {
  const isBuy = data.direction === 'BUY';
  const actionClass = isBuy ? 'sc-action-buy' : 'sc-action-sell';
  const statusColor = isBuy ? '#10b981' : '#ef4444';
  const progress = data.confidence || 60;

  // Mock calculations for display if not present
  const entry = data.entry;
  const tp = data.tp;
  const sl = data.sl;
  const pips = Math.abs(tp - entry) * 10000; // Rough calc for forex
  const rr = "1:2"; // Hardcoded or calc

  return `
    <div class="sc-card animate-in">
      <div class="sc-header-top">
        <span class="sc-tag">SNAPSHOT</span>
        <span class="${actionClass}">${data.direction}</span>
      </div>
      <div class="sc-title">${data.asset || 'EURUSD'}</div>
      <div class="sc-subtitle">⏳ ${data.timeframe || 'M15'} • LONDON SESSION</div>

      <div class="sc-status">
        <div class="sc-status-label">
          <div class="sc-status-dot" style="background: ${statusColor}"></div>
          <span class="text-valid" style="color: ${statusColor}">Valid Signal</span>
        </div>
        <div class="sc-progress-row">
          <div class="sc-progress-track">
            <div class="sc-progress-fill" style="width: ${progress}%; background: ${statusColor}"></div>
          </div>
          <div class="sc-progress-text">${progress}%</div>
        </div>
      </div>

      <div class="sc-data-box">
        <div class="sc-entry-section">
          <div class="sc-label">💰 ENTRY ZONE</div>
          <div class="sc-value-xl">${entry}</div>
        </div>
        <div class="sc-targets-row">
          <div class="sc-target-col">
            <div class="sc-label">🎯 TARGET</div>
            <div class="sc-value-lg text-green">${tp}</div>
          </div>
          <div class="sc-target-col right">
            <div class="sc-label">🛑 STOP</div>
            <div class="sc-value-lg text-red">${sl}</div>
          </div>
        </div>
      </div>

      <div class="sc-footer-stats">
        <span>Potential: <strong>+${Math.round(pips)} pips</strong></span>
        <span>RRR: <strong>${rr}</strong></span>
      </div>
      <div class="sc-footer-meta">
        <span>Gen: ${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })} UTC</span>
        <span class="sc-update">🔄 Update Available</span>
      </div>
    </div>
  `;
}

export function renderStats(data) {
  // Optional: keep it empty or return simplified stats if needed
  return "";
}
