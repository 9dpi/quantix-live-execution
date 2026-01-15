function renderSignalCard(data) {
  const p = data.payload;
  const dirClass = p.direction.toLowerCase();

  return `
    <div class="signal-card">
      <div class="signal-header">
        <div class="asset">${p.asset}</div>
        <div class="direction ${dirClass}">${p.direction}</div>
      </div>

      <div class="confidence">
        Confidence: <strong>${p.confidence}%</strong>
      </div>

      <div class="levels">
        <div class="level">
          <span>ENTRY</span>
          ${p.entry[0]} – ${p.entry[1]}
        </div>
        <div class="level">
          <span>TAKE PROFIT</span>
          ${p.tp}
        </div>
        <div class="level">
          <span>STOP LOSS</span>
          ${p.sl}
        </div>
        <div class="level">
          <span>TIMEFRAME</span>
          ${p.timeframe}
        </div>
      </div>

      <div class="meta">
        <div>${p.session}</div>
        <div>${p.source}</div>
      </div>
    </div>
  `;
}
