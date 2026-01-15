// Signal Genius AI - Frontend Logic
// Auto-refresh every 10 seconds

const CONFIG = {
    API_ENDPOINT: '/api/v1/lab/market-reference',
    REFRESH_INTERVAL: 10000, // 10 seconds
    SYMBOL: 'EURUSD',
    TIMEFRAME: 'M15'
};

let refreshTimer = null;
let lastUpdateTime = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Signal Genius AI - Initializing...');
    loadSignal();
    startAutoRefresh();
    updateRefreshIndicator();
});

// Load signal data
async function loadSignal() {
    try {
        // For now, use mock data since API is not ready
        const signal = await fetchSignalData();

        if (signal && signal.confidence >= 95) {
            renderSignal(signal);
        } else {
            renderWaitingState();
        }

        lastUpdateTime = new Date();
    } catch (error) {
        console.error('Error loading signal:', error);
        renderWaitingState();
    }
}

// Fetch signal data (mock for now)
async function fetchSignalData() {
    // TODO: Replace with actual API call when backend is ready
    // const response = await fetch(`${CONFIG.API_ENDPOINT}?symbol=${CONFIG.SYMBOL}&tf=${CONFIG.TIMEFRAME}`);
    // return await response.json();

    // Mock data for demonstration
    return getMockSignal();
}

// Mock signal generator
function getMockSignal() {
    const now = new Date();
    const confidence = 96; // High confidence for demo

    if (confidence < 95) {
        return null;
    }

    return {
        asset: "EUR/USD",
        direction: "BUY",
        direction_icon: "🟢",
        timeframe: "M15",
        session: "London → New York Overlap",

        price_levels: {
            entry_zone: ["1.16710", "1.16750"],
            take_profit: "1.17080",
            stop_loss: "1.16480"
        },

        trade_details: {
            target_pips: 35,
            risk_reward: "1 : 1.40",
            suggested_risk: "0.5% – 1%"
        },

        trade_type: "Intraday",
        confidence: confidence,

        posted_at_utc: now.toISOString(),

        expiry_rules: {
            session_only: true,
            expires_at: "NY_CLOSE",
            invalidate_if_missed_entry: true
        },

        disclaimer: "Not financial advice. Trade responsibly."
    };
}

// Render signal card
function renderSignal(signal) {
    const container = document.getElementById('signal-container');
    const directionClass = signal.direction.toLowerCase();

    const html = `
    <div class="bento-card signal-card animate-in">
      <div class="signal-header">
        <div>
          <h2 class="asset-name">${signal.asset}</h2>
          <div class="detail-label">
            ⏳ Timeframe: <strong>${signal.timeframe}</strong> | 🌍 ${signal.session}
          </div>
        </div>
        <div class="direction-badge ${directionClass}">
          ${signal.direction_icon} ${signal.direction}
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
              <span class="confidence-badge">${signal.confidence}% ⭐</span>
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
        <small style="color: var(--text-secondary);">⚠️ ${signal.disclaimer}</small>
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
        <div class="waiting-icon">🕒</div>
        <h3 class="waiting-title">No High-Confidence Signal Yet</h3>
        <p class="waiting-description">
          Signal Genius AI only publishes signals when AI Confidence ≥ 95%.
          <br><br>
          The system is continuously analyzing EUR/USD M15 market conditions.
          Check back soon or wait for our Telegram notification.
        </p>
      </div>
    </div>
  `;

    container.innerHTML = html;
}

// Start auto-refresh
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }

    refreshTimer = setInterval(() => {
        console.log('🔄 Auto-refreshing signal...');
        loadSignal();
    }, CONFIG.REFRESH_INTERVAL);

    console.log(`✅ Auto-refresh enabled (every ${CONFIG.REFRESH_INTERVAL / 1000}s)`);
}

// Update refresh indicator
function updateRefreshIndicator() {
    setInterval(() => {
        const indicator = document.getElementById('refresh-indicator');
        if (indicator && lastUpdateTime) {
            const secondsAgo = Math.floor((new Date() - lastUpdateTime) / 1000);
            const nextRefresh = Math.max(0, CONFIG.REFRESH_INTERVAL / 1000 - secondsAgo);
            indicator.textContent = `Next refresh in ${nextRefresh}s`;
        }
    }, 1000);
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
