const CONFIG = {
  API_ENDPOINT: 'https://signalgeniusai-production.up.railway.app/api/v1/signal/latest',
  SYMBOL: 'EUR/USD',
  TIMEFRAME: 'M15'
};

let refreshTimer = null;
let lastUpdateTime = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Signal Genius AI - Initializing...');
  initTheme();
  loadSignal();
  startAutoRefresh();
});

function startAutoRefresh() {
  console.log("[AutoRefresh] Enabled (10s)");
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(() => {
    loadSignal();
  }, 10000);
}

// Theme Management
function initTheme() {
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;
  const themeIcon = themeToggle.querySelector('.theme-icon');

  // Check saved theme
  const savedTheme = localStorage.getItem('theme') || 'dark';
  body.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme, themeIcon);

  themeToggle.addEventListener('click', () => {
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme, themeIcon);
  });
}

function updateThemeIcon(theme, iconElement) {
  iconElement.textContent = theme === 'dark' ? '🌙' : '☀️';
}

// Load signal data with Snapshot-First Strategy
async function loadSignal() {
  // 1️⃣ Default state is already SKELETON (rendered in HTML)
  // We only check cache or fetch.

  const cached = localStorage.getItem('latest_signal');
  if (cached) {
    console.log('⚡ Rendered cached snapshot');
    renderSignal(JSON.parse(cached), true); // true = isCached
  }

  // 2️⃣ Fetch Fresh Data in Background
  try {
    const signal = await fetchSignalData();

    if (signal) {
      if (signal.confidence >= 95) {
        // 3️⃣ Update UI with fresh data
        renderSignal(signal, false); // false = isLive (Live Update)
        localStorage.setItem('latest_signal', JSON.stringify(signal));
      } else {
        // Valid but low confidence signal.
        // If we don't have a cache, show Waiting State.
        if (!cached) {
          renderWaitingState();
        }
      }
    } else {
      // Signal explicitly null (e.g. backend turned off signal generation)
      if (!cached) {
        renderWaitingState();
      }
    }
  } catch (error) {
    console.error('Background fetch failed:', error);
    // 4️⃣ Fail handling: 
    // If we have cache, we keep showing it (Snapshot mode).
    // If NO cache, we must remove Skeleton and show Waiting/Error state.
    if (!cached) {
      renderWaitingState();
    }
  }
}


// Fetch signal data from Railway API
async function fetchSignalData() {
  try {
    const response = await fetch(`${CONFIG.API_ENDPOINT}?symbol=${CONFIG.SYMBOL}&tf=${CONFIG.TIMEFRAME}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (data.message) {
      return null;
    }

    return data;
  } catch (error) {
    console.warn('API call failed, falling back to mock or cache:', error);
    // Fallback to mock data ONLY if enabled/needed for demo
    // return getMockSignal(); 
    return null;
  }
}

// Render signal card
function renderSignal(signal, isCached = false) {
  const container = document.getElementById('signal-container');
  const directionClass = signal.direction.toLowerCase();

  // Confidence Tier Logic
  const isExperimental = signal.confidence_tier === 'MEDIUM';
  const tierColor = signal.tier_color === 'green' ? '#10b981' : (signal.tier_color === 'yellow' ? '#ffc107' : '#94a3b8');

  // Warning Banner for Experimental Signals
  const riskBanner = isExperimental
    ? `<div class="experimental-banner" style="background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); padding: 12px; border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem;">⚠️</span>
        <div style="font-size: 0.85rem; color: #ffc107; line-height: 1.4; font-weight: 500;">
          <strong>Experimental AI Insight:</strong><br>
          ${signal.risk_note}
        </div>
      </div>`
    : '';

  // UX Copy Definitions
  const statusBadge = isCached
    ? `<span class="status-badge cached" style="background: rgba(255, 193, 7, 0.1); color: #ffc107; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; border: 1px solid rgba(255, 193, 7, 0.2);">⚡ AI SNAPSHOT LOADED</span>`
    : `<span class="status-badge live" style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.2);">🟢 LIVE UPDATE</span>`;

  const html = `
    <div class="bento-card signal-card animate-in">
      ${riskBanner}
      
      <div class="signal-header">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <h2 class="asset-name" style="margin-bottom: 0;">${signal.asset}</h2>
            ${statusBadge}
          </div>
          <div class="detail-label">
            ⏳ Timeframe: <strong>${signal.timeframe}</strong> | 🌍 ${signal.session}
          </div>
        </div>
        <div class="direction-badge ${directionClass}" style="border-color: ${tierColor}; color: ${tierColor};">
          ${signal.direction_icon} ${signal.tier_label || signal.direction}
        </div>
      </div>
      
      <div class="signal-details">
        <div class="detail-group">
          <div class="detail-label">💰 Price Levels</div>
          <div class="price-levels">
            <div class="price-item">
              <span class="price-label">Entry Zone:</span>
              <span class="price-value">${signal.price_levels.entry_zone[0]} – ${signal.price_levels.entry_zone[1]}</span>
            </div>
            <div class="price-item">
              <span class="price-label">Take Profit:</span>
              <span class="price-value" style="color: var(--accent-green)">${signal.price_levels.take_profit}</span>
            </div>
            <div class="price-item">
              <span class="price-label">Stop Loss:</span>
              <span class="price-value" style="color: #ff4444">${signal.price_levels.stop_loss}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-group">
          <div class="detail-label">📏 Trade Details</div>
          <div class="price-levels">
            <div class="price-item">
              <span class="price-label">Target:</span>
              <span class="price-value">+${signal.trade_details.target_pips} pips</span>
            </div>
            <div class="price-item">
              <span class="price-label">Risk–Reward:</span>
              <span class="price-value">${signal.trade_details.risk_reward}</span>
            </div>
            <div class="price-item">
              <span class="price-label">Suggested Risk:</span>
              <span class="price-value">${signal.trade_details.suggested_risk}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-group">
          <div class="detail-label">🕒 Trade Info</div>
          <div class="price-levels">
            <div class="price-item">
              <span class="price-label">Type:</span>
              <span class="price-value">${signal.trade_type}</span>
            </div>
            <div class="price-item">
              <span class="price-label">Posted:</span>
              <span class="price-value">${formatDateTime(signal.posted_at_utc)}</span>
            </div>
            <div class="price-item">
              <span class="price-label">AI Confidence:</span>
              <span class="confidence-badge" style="color: ${tierColor}">⭐ ${signal.confidence}%</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="expiry-rules">
        <h4>⏳ Auto-Expiry Rules</h4>
        <ul>
          <li>Signal is valid for this session only</li>
          <li>Expires at New York close or if TP or SL is hit</li>
          <li>Do not enter if price has already moved significantly beyond the entry zone</li>
        </ul>
      </div>
      
      <div style="text-align: center; margin-top: var(--spacing-md); padding-top: var(--spacing-md); border-top: 1px solid var(--border-color);">
        <small style="color: var(--text-secondary); opacity: 0.8;">${signal.risk_note}</small>
        <br>
        <small style="color: var(--text-secondary); opacity: 0.6; font-size: 0.7rem; display: block; margin-top: 8px;">⚠️ ${signal.disclaimer}</small>
      </div>
    </div>
  `;

  container.innerHTML = html;
}

// Render waiting state
function renderWaitingState() {
  const container = document.getElementById('signal-container');

  const html = `
    <div class="bento-card signal-card animate-in">
      <div class="waiting-state">
        <div class="waiting-icon" style="color: var(--primary-cyan)">🎯</div>
        <h3 class="waiting-title" style="font-weight: 800; color: var(--text-primary);">Scanning Market...</h3>
        <p class="waiting-description" style="color: var(--text-secondary); font-weight: 500;">
          Signal Genius AI is analyzing EUR/USD market liquidity and momentum.
          <br><br>
          <span style="color: var(--primary-cyan); font-weight: 700;">Wait for 95% + Confidence.</span>
        </p>
      </div>
    </div>
  `;

  container.innerHTML = html;
}

// Format date time
function formatDateTime(isoString) {
  const date = new Date(isoString);
  const options = {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC'
  };
  return date.toLocaleString('en-US', options) + ' UTC';
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    loadSignal,
    getMockSignal,
    formatDateTime
  };
}
