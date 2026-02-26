// UPDATED: Pointing to Quantix Core (Validation Backend)
const API_BASE = 'https://quantixaicore-production.up.railway.app';
let pHistory = [];
let livePrice = null;
let prevPrice = 0;
let activeTab = 'overview'; // Default to overview

// Pagination State
let allHistory = [];
let currentPage = 1;
const itemsPerPage = 10;

// --- UTILS ---

function calcConfidence(val) {
    if (val === undefined || val === null) return 0;
    if (val <= 1.2) return Math.round(val * 100);
    return Math.round(val);
}

function calculateRR(entry, sl, tp, direction) {
    if (!entry || !sl || !tp) return "n/a";
    try {
        const r = Math.abs(entry - sl);
        const rwd = Math.abs(tp - entry);
        if (r === 0) return "1.00";
        return (rwd / r).toFixed(2);
    } catch (e) { return "n/a"; }
}

function getTradingViewLink(symbol, timeframe) {
    if (!symbol) return "#";
    const cleanSymbol = symbol.replace('/', '');
    const tvSymbol = cleanSymbol.includes(':') ? cleanSymbol : `FX:${cleanSymbol}`;
    const tf = timeframe ? timeframe.replace('M', '') : '15';
    return `https://www.tradingview.com/chart/?symbol=${tvSymbol}&interval=${tf}`;
}

// --- TRADINGVIEW MODAL LOGIC ---

window.openTVPreview = (symbol, timeframe, entry, sl, tp, generated_at) => {
    const modal = document.getElementById('tv-modal');
    const iframe = document.getElementById('tv-iframe');

    document.getElementById('modal-title').innerText = `${symbol} \u00b7 ${timeframe} \u00b7 TradingView Preview`;
    document.getElementById('modal-entry').innerText = parseFloat(entry).toFixed(5);
    document.getElementById('modal-sl').innerText = parseFloat(sl).toFixed(5);
    document.getElementById('modal-tp').innerText = parseFloat(tp).toFixed(5);

    const dt = new Date(generated_at);
    document.getElementById('modal-utc').innerText = dt.toISOString().replace('T', ' ').slice(0, 16);
    document.getElementById('modal-external-link').href = getTradingViewLink(symbol, timeframe);

    const cleanSymbol = symbol.replace('/', '');
    const tvSymbol = cleanSymbol.includes(':') ? cleanSymbol : `FX:${cleanSymbol}`;
    const tf = timeframe ? timeframe.replace('M', '') : '15';
    iframe.src = `https://s.tradingview.com/widgetembed/?symbol=${tvSymbol}&interval=${tf}&theme=dark`;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
};

window.closeTVModal = () => {
    const modal = document.getElementById('tv-modal');
    const iframe = document.getElementById('tv-iframe');
    iframe.src = "";
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
};

document.addEventListener('click', (e) => {
    const modal = document.getElementById('tv-modal');
    if (e.target === modal) closeTVModal();
});

// Tab Switching Logic
window.switchTab = (tab) => {
    activeTab = tab;

    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (tab === 'logs' && (link.innerText.includes('Logs') || link.innerText.includes('System Logs'))) {
            link.classList.add('active');
        } else if (tab === 'overview' && link.innerText.includes('Overview')) {
            link.classList.add('active');
        }
    });

    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const target = document.getElementById(`${tab}-tab`);
    if (target) target.classList.add('active');

    if (tab === 'overview') loadHistory();
    if (tab === 'logs') fetchLogs();
};

// --- DATA FETCHING ---

function isMarketOpen() {
    const now = new Date();
    const day = now.getUTCDay();
    const hour = now.getUTCHours();
    if (day === 6) return false;
    if (day === 5 && hour >= 22) return false;
    if (day === 0 && hour < 22) return false;
    return true;
}

// Updated Core API Path using global CONFIG
const AI_CORE_API = window.CONFIG?.AI_CORE_API || `${API_BASE}/api/v1`;

// --- DATA FETCHING FALLBACK SYSTEM ---

async function fetchWithFallback(endpoint, options = {}) {
    try {
        const url = endpoint.startsWith('http') ? endpoint : `${AI_CORE_API}${endpoint}`;

        // Ensure JSON headers for POST
        if (options.method === 'POST' && options.body && !options.headers) {
            options.headers = { 'Content-Type': 'application/json' };
        }

        const res = await fetch(url, { ...options, timeout: 5000 });
        if (res.ok) return await res.json();
        throw new Error(`HTTP ${res.status}`);
    } catch (error) {
        if (window.CONFIG?.USE_SUPABASE_FALLBACK) {
            console.warn(`⚠️ API failed for ${endpoint}, falling back to Supabase:`, error.message);
            return await fetchFromSupabase(endpoint);
        }
        throw error;
    }
}

async function fetchFromSupabase(endpoint) {
    const baseUrl = window.CONFIG.SUPABASE_REST;
    const headers = {
        'apikey': window.CONFIG.SUPABASE_KEY,
        'Authorization': `Bearer ${window.CONFIG.SUPABASE_KEY}`,
        'Content-Type': 'application/json'
    };

    if (endpoint.includes('/signals/latest')) {
        // Fetch active signals
        const activeRes = await fetch(`${baseUrl}/fx_signals?state=in.("WAITING_FOR_ENTRY","ENTRY_HIT")&telegram_message_id=not.is.null&select=*&order=generated_at.desc&limit=1`, { headers });
        const activeData = await activeRes.json();

        // Fetch history
        const histRes = await fetch(`${baseUrl}/fx_signals?state=not.in.("WAITING_FOR_ENTRY","ENTRY_HIT")&telegram_message_id=not.is.null&select=*&order=generated_at.desc&limit=50`, { headers });
        const histData = await histRes.json();

        return { success: true, active: activeData[0] || null, history: histData };
    }

    if (endpoint.includes('/telemetry')) {
        const statsRes = await fetch(`${baseUrl}/fx_signals?select=state,ai_confidence`, { headers });
        const data = await statsRes.json();

        const total = data.length;
        const wins = data.filter(s => s.state === 'TP_HIT').length;
        const losses = data.filter(s => s.state === 'SL_HIT').length;
        const win_rate = total > 0 ? (wins / (wins + losses) * 100).toFixed(1) : 0;

        return {
            total_samples: total,
            performance: { total_signals: total, wins, losses, win_rate }
        };
    }

    if (endpoint.includes('/analysis-logs')) {
        const res = await fetch(`${baseUrl}/fx_analysis_log?select=*&order=timestamp.desc&limit=20`, { headers });
        return { success: true, data: await res.json() };
    }

    if (endpoint.includes('/validation-logs')) {
        const res = await fetch(`${baseUrl}/fx_signal_validation?select=*&order=created_at.desc&limit=20`, { headers });
        return { success: true, data: await res.json() };
    }

    if (endpoint.includes('/signal/notify')) {
        console.log("ℹ️ Signal notification (Fallback Mode): Supabase record exists, but direct API notification skipped.");
        return { success: true };
    }

    return { success: false, error: "Cloud connection lost and no local fallback for this endpoint." };
}

async function fetchLatestSignal() {
    const recordEl = document.getElementById('signal-record');
    const closedEl = document.getElementById('market-closed');
    const scanningEl = document.getElementById('no-signal-view');

    if (!isMarketOpen()) {
        if (recordEl) recordEl.style.display = 'none';
        if (scanningEl) scanningEl.style.display = 'none';
        if (closedEl) closedEl.style.display = 'flex';
        return;
    }

    try {
        const json = await fetchWithFallback('/signals/latest');

        if (json.active) {
            currentActiveRecord = json.active;
            displayActiveSignal(json.active);
        } else {
            currentActiveRecord = null;
            if (recordEl) recordEl.style.display = 'none';
            if (closedEl) closedEl.style.display = 'none';
            if (scanningEl) scanningEl.style.display = 'flex';
        }

        // If history was returned in the same packet, update it
        if (json.history && allHistory.length === 0) {
            allHistory = json.history;
            renderHistoryPage();
        }
    } catch (error) {
        console.error("Fetch failed:", error);
    }
}

function displayActiveSignal(record) {
    const recordEl = document.getElementById('signal-record');
    if (!recordEl) return;

    recordEl.style.display = 'flex';
    document.getElementById('market-closed').style.display = 'none';
    document.getElementById('no-signal-view').style.display = 'none';

    const asset = record.asset || 'EURUSD';
    const tf = record.timeframe || 'M15';
    const direction = (record.direction || record.side || 'BUY').toUpperCase();
    const entry = record.entry_price || record.entry || 0;
    const tp = record.tp || record.take_profit || 0;
    const sl = record.sl || record.stop_loss || 0;
    const conf = calcConfidence(record.release_confidence || 0);

    const entryLimit = record.activation_limit_mins || 35;
    const maxTrade = record.max_monitoring_mins || 90;
    document.getElementById('record-entry-duration').textContent = `${entryLimit}m`;
    document.getElementById('record-max-duration').textContent = `${maxTrade}m`;
    document.getElementById('record-warning-time').textContent = maxTrade;

    document.getElementById('record-asset').textContent = asset;
    document.getElementById('record-tf').textContent = tf;

    const dirText = direction === 'BUY' ? '\uD83D\uDFE2 BUY' : '\uD83D\uDD34 SELL';
    document.getElementById('record-direction-text').textContent = dirText;
    document.getElementById('record-direction-text').style.color = direction === 'BUY' ? 'var(--trade-up)' : 'var(--trade-down)';

    document.getElementById('record-entry').textContent = parseFloat(entry).toFixed(5);
    document.getElementById('record-tp').textContent = parseFloat(tp).toFixed(5);
    document.getElementById('record-sl').textContent = parseFloat(sl).toFixed(5);
    document.getElementById('record-confidence').textContent = `${conf}%`;

    const state = (record.status || record.state || 'WAITING').toUpperCase();
    const statusBadge = document.getElementById('record-status-badge');
    const realTimeStatus = getStatusLabel(record, livePrice);

    if (realTimeStatus === 'Waiting...') {
        statusBadge.textContent = 'WAITING FOR ENTRY';
        statusBadge.style.color = 'var(--quantix-accent)';
    } else if (realTimeStatus === 'Entry Hit' || realTimeStatus === 'Live Trade') {
        statusBadge.textContent = 'LIVE TRADE';
        statusBadge.style.color = 'var(--trade-up)';
    } else {
        statusBadge.textContent = realTimeStatus.toUpperCase();
        statusBadge.style.color = (realTimeStatus === 'TP Hit') ? 'var(--trade-up)' : (realTimeStatus === 'SL Hit' ? 'var(--trade-down)' : 'var(--text-secondary)');
    }

    // TRIGGER NOTIFICATION IF HIT
    if (['Entry Hit', 'TP Hit', 'SL Hit'].includes(realTimeStatus)) {
        notifyStatusChange(record, realTimeStatus);
    }
}

// Global store for the active signal object to allow real-time monitoring
let currentActiveRecord = null;

async function loadHistory() {
    const tbody = document.getElementById('history-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center">⏳ Fetching History from Quantix Core...</td></tr>';

    try {
        const json = await fetchWithFallback('/signals/latest');

        // Check success flag or direct history array
        if (json.success === false) throw new Error(json.error || json.message);

        allHistory = json.history || [];
        allHistory.sort((a, b) => new Date(b.generated_at) - new Date(a.generated_at));
        currentPage = 1;
        renderHistoryPage();

    } catch (e) {
        console.error("History fetch error:", e);
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color:var(--trade-down)">⚠️ Error loading history: ${e.message}</td></tr>`;
    }
}


function renderHistoryPage() {
    const tbody = document.getElementById('history-body');
    const pageInfo = document.getElementById('page-info');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (!tbody) return;
    tbody.innerHTML = "";

    if (allHistory.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding: 2rem;">No released signals in this period.</td></tr>';
        if (pageInfo) pageInfo.innerText = "Page 0 of 0";
        return;
    }

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = allHistory.slice(startIndex, endIndex);

    pageData.forEach((sig, index) => {
        const dt = new Date(sig.generated_at);
        const dStr = dt.toLocaleDateString('en-CA', { timeZone: 'UTC' });
        const tStr = dt.toLocaleTimeString('en-GB', { hour12: false, timeZone: 'UTC' }).slice(0, 5);

        const entry = sig.entry_price || sig.entry || 0;
        const sl = sig.stop_loss || sig.sl || 0;
        const tp = sig.take_profit || sig.tp || 0;
        const direction = (sig.direction || sig.side || 'BUY').toUpperCase();
        const conf = calcConfidence(sig.release_confidence || 0);

        let closedStr = "--:--";
        if (sig.closed_at) {
            const cdt = new Date(sig.closed_at);
            closedStr = cdt.toLocaleTimeString('en-GB', { hour12: false, timeZone: 'UTC' }).slice(0, 5);
        }

        const statusLabel = getStatusLabel(sig, index === 0 ? livePrice : null);
        const pips = getPipsInfo(sig, index === 0 ? livePrice : null);

        let resClass = 'neut';
        let confColor = 'var(--quantix-accent)';

        if (sig.result === 'PROFIT' || sig.status === 'CLOSED_TP') {
            resClass = 'up';
            confColor = 'var(--text-secondary)';
        } else if (sig.result === 'LOSS' || sig.status === 'CLOSED_SL') {
            resClass = 'down';
            confColor = 'var(--text-secondary)';
        } else if (sig.status === 'EXPIRED' || sig.status === 'CLOSED_TIMEOUT' || (sig.state && sig.state.includes('EXPIRED'))) {
            resClass = 'expired';
            confColor = 'var(--text-secondary)';
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="mono" style="font-size: 0.8rem">${dStr} ${tStr}</td>
            <td><span class="pill ${direction === 'BUY' ? 'up' : 'down'}">${direction}</span></td>
            <td class="mono" style="font-weight:700; color:${confColor}">${conf}%</td>
            <td class="mono">${parseFloat(entry).toFixed(5)}</td>
            <td class="mono" style="color:var(--trade-up)">${parseFloat(tp).toFixed(5)}</td>
            <td class="mono" style="color:var(--trade-down)">${parseFloat(sl).toFixed(5)}</td>
            <td class="mono" style="font-weight:700; color:${pips.color}">${pips.label}</td>
            <td class="mono" style="font-size: 0.75rem">${closedStr}</td>
            <td><span class="pill ${resClass}" style="min-width:80px; text-align:center">${statusLabel}</span></td>
        `;
        tbody.appendChild(row);
    });

    const totalPages = Math.ceil(allHistory.length / itemsPerPage);
    if (pageInfo) pageInfo.innerText = `Page ${currentPage} of ${totalPages}`;

    if (prevBtn) prevBtn.disabled = (currentPage === 1);
    if (nextBtn) nextBtn.disabled = (currentPage === totalPages || totalPages === 0);
}

function changePage(dir) {
    const totalPages = Math.ceil(allHistory.length / itemsPerPage);
    const newPage = currentPage + dir;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        renderHistoryPage();
    }
}

function getStatusLabel(s, currentPrice = null) {
    if (!s) return '--';
    const status = (s.status || s.state || '').toUpperCase();
    const result = (s.result || '').toUpperCase();
    const direction = (s.direction || s.side || 'BUY').toUpperCase();

    // 1. Check Age Expiration (Safety Fallback)
    const genTime = s.generated_at || s.timestamp;
    if (genTime) {
        const ageHours = (new Date() - new Date(genTime)) / (1000 * 60 * 60);
        if (ageHours > 3 && (status === 'WAITING' || status === 'WAITING_FOR_ENTRY' || status === 'PUBLISHED' || status === 'ACTIVE' || status === 'ENTRY_HIT')) {
            if (result === 'UNKNOWN' || result === '') return 'Expired';
        }
    }

    // 2. Real-time Detection
    const isWaiting = (status === 'WAITING' || status === 'WAITING_FOR_ENTRY' || status === 'PUBLISHED');
    const isActive = (status === 'ACTIVE' || status === 'ENTRY_HIT');

    if (currentPrice && (isWaiting || isActive)) {
        const entry = parseFloat(s.entry_price || s.entry || 0);
        const tp = parseFloat(s.tp || s.take_profit || 0);
        const sl = parseFloat(s.sl || s.stop_loss || 0);

        if (direction === 'BUY') {
            // Can only hit TP/SL if already active
            if (isActive) {
                if (currentPrice >= tp) return 'TP Hit';
                if (currentPrice <= sl) return 'SL Hit';
            }
            // Check for entry hit while waiting
            if (isWaiting && currentPrice <= entry) return 'Entry Hit';
        } else {
            if (isActive) {
                if (currentPrice <= tp) return 'TP Hit';
                if (currentPrice >= sl) return 'SL Hit';
            }
            if (isWaiting && currentPrice >= entry) return 'Entry Hit';
        }
    }

    if (result === 'PROFIT' || status === 'CLOSED_TP') return 'TP Hit';
    if (result === 'LOSS' || status === 'CLOSED_SL') return 'SL Hit';
    if (status === 'CLOSED_TIMEOUT') return 'Timeout';
    if (status === 'EXPIRED') return 'Expired';
    if (status === 'ACTIVE' || status === 'ENTRY_HIT') return 'Live Trade';
    if (status === 'WAITING' || status === 'WAITING_FOR_ENTRY' || status === 'PUBLISHED') return 'Waiting...';
    return status.replace(/_/g, ' ');
}

// Track last known status to prevent duplicate notifications
let lastStatusTriggered = null;
let currentActiveSignalId = null;

async function notifyStatusChange(signal, newStatus) {
    if (lastStatusTriggered === newStatus && currentActiveSignalId === signal.id) return;

    lastStatusTriggered = newStatus;
    currentActiveSignalId = signal.id;

    console.log(`🔔 Sending Telegram Alert: ${newStatus} for #${signal.id}`);

    try {
        await fetchWithFallback('/signal/notify', {
            method: 'POST',
            body: JSON.stringify({
                signal: signal,
                status: newStatus,
                price: livePrice
            })
        });
    } catch (e) {
        console.warn("Notification failed:", e);
    }
}

function getPipsInfo(s, currentPrice = null) {
    const entry = parseFloat(s.entry_price || s.entry || 0);
    const tp = parseFloat(s.tp || s.take_profit || 0);
    const sl = parseFloat(s.sl || s.stop_loss || 0);
    const result = (s.result || '').toUpperCase();
    const status = (s.status || s.state || '').toUpperCase();
    const direction = (s.direction || s.side || 'BUY').toUpperCase();

    let dist = 0;
    let label = '--';
    let color = 'var(--text-secondary)';

    if (result === 'PROFIT' || status === 'CLOSED_TP') {
        dist = Math.abs(entry - tp);
        label = `+${Math.round(dist * 10000 * 10) / 10} pips`;
        color = 'var(--trade-up)';
    } else if (result === 'LOSS' || status === 'CLOSED_SL') {
        dist = -Math.abs(entry - sl);
        label = `${Math.round(dist * 10000 * 10) / 10} pips`;
        color = 'var(--trade-down)';
    } else if (currentPrice && (status === 'ACTIVE' || status === 'ENTRY_HIT')) {
        // Floating Pips Calculation (Match Telesignal Logic)
        const diff = direction === 'BUY' ? (currentPrice - entry) : (entry - currentPrice);
        const pipsValue = Math.round(diff * 10000 * 10) / 10;
        label = `${pipsValue >= 0 ? '+' : ''}${pipsValue} pips`;
        color = pipsValue >= 0 ? 'var(--trade-up)' : 'var(--trade-down)';
    }

    return { label, color };
}

function updateHistoryClock() {
    const el = document.getElementById('dynamic-history-title');
    if (!el) return;
    const now = new Date();
    const utcStr = now.getUTCFullYear() + '-' +
        String(now.getUTCMonth() + 1).padStart(2, '0') + '-' +
        String(now.getUTCDate()).padStart(2, '0') + ' ' +
        String(now.getUTCHours()).padStart(2, '0') + ':' +
        String(now.getUTCMinutes()).padStart(2, '0') + ':' +
        String(now.getUTCSeconds()).padStart(2, '0');
    el.innerHTML = `Live Executions <span style="font-size: 0.8rem; color: #475569; font-weight: 500; margin-left: 8px;">[ ${utcStr} UTC ]</span>`;
}


async function fetchLogs() {
    const tbody = document.getElementById('logs-body');
    if (!tbody) return;

    // Also refresh heartbeat
    fetchHeartbeat();

    try {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px; color:var(--text-secondary)">Loading validation data...</td></tr>';

        const json = await fetchWithFallback('/validation-logs?limit=50');
        if (json.success && json.data) {
            tbody.innerHTML = '';
            if (json.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px; color:var(--text-secondary)">No validation events recorded yet (Waiting for first signal).</td></tr>';
                return;
            }
            json.data.forEach(log => {
                const tr = document.createElement('tr');
                const isDisc = log.is_discrepancy;
                const statusColor = isDisc ? 'var(--trade-down)' : 'var(--trade-up)';
                const statusIcon = isDisc ? '⚠️' : '✅';
                const statusText = isDisc ? 'PRICE MISMATCH' : 'PRICE MATCHED';

                let ts = new Date(log.created_at).toLocaleString('en-GB', { timeZone: 'UTC' });

                // Proof (Candle Data)
                let proof = '';
                if (log.validator_candle) {
                    const c = log.validator_candle;
                    proof = `O:${c.open} H:${c.high} L:${c.low} C:${c.close}`;
                } else {
                    proof = 'No Candle Data';
                }

                let meta = log.meta_data ? (typeof log.meta_data === 'string' ? log.meta_data : JSON.stringify(log.meta_data)) : '';

                tr.innerHTML = `
                    <td style="color:var(--text-secondary); font-family:var(--font-mono); font-size:0.75rem">${ts}</td>
                    <td style="color:var(--quantix-accent)">${log.signal_id ? log.signal_id.slice(0, 4) : '--'}</td>
                    <td>${log.check_type || 'UNKNOWN'}</td>
                    <td style="font-family:var(--font-mono)">${Number(log.validator_price || 0).toFixed(5)}</td>
                    <td style="color:${statusColor}; font-weight:700;">${statusIcon} ${statusText}</td>
                    <td style="color:var(--text-secondary); font-size:0.7rem; font-family:var(--font-mono);">
                        <div style="font-weight:bold; color:var(--text-primary)">Proof: ${proof}</div>
                        <div style="margin-top:2px;">${meta}</div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:var(--text-secondary)">Quantix AI Core is updating or offline. Retrying...</td></tr>`;
    }
}

async function fetchHeartbeat() {
    const hbody = document.getElementById('heartbeat-body');
    if (!hbody) return;

    try {
        const json = await fetchWithFallback('/analysis-logs?limit=20');

        if (json.success && json.data) {
            hbody.innerHTML = '';
            json.data.forEach(beat => {
                const tr = document.createElement('tr');
                const ts = new Date(beat.timestamp).toLocaleTimeString('en-GB', { hour12: false, timeZone: 'UTC' });
                const conf = Math.round((beat.release_confidence || beat.confidence) * 100);
                const strength = Math.round(beat.strength * 100);
                const color = conf >= 65 ? 'var(--trade-up)' : 'var(--text-secondary)';

                tr.innerHTML = `
                    <td style="color:var(--text-secondary); font-family:var(--font-mono); font-size:0.75rem">${ts}</td>
                    <td style="font-weight:700">${beat.asset}</td>
                    <td style="color:${color}; font-weight:700">${beat.status}</td>
                    <td style="font-family:var(--font-mono); font-weight:700; color:${color}">${conf}%</td>
                    <td style="font-family:var(--font-mono); color:var(--text-secondary)">${strength}%</td>
                    <td style="color:var(--text-secondary); font-size:0.7rem; font-style:italic">${beat.refinement || 'Standard scan'}</td>
                `;
                hbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.warn("Heartbeat fetch failed");
    }
}

// Export for HTML
window.fetchLogs = fetchLogs;

// Initial Run
document.addEventListener('DOMContentLoaded', () => {
    updateHistoryClock();
    setInterval(updateHistoryClock, 1000);
    fetchLatestSignal();
    loadHistory();

    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (prevBtn) prevBtn.addEventListener('click', () => changePage(-1));
    if (nextBtn) nextBtn.addEventListener('click', () => changePage(1));

    setInterval(() => {
        if (activeTab === 'overview' || activeTab === 'active') fetchLatestSignal();
        if (activeTab === 'logs') fetchLogs();
    }, 10000); // Increased sync to 10s to match Telesignal

    initPriceFeed();
});

// === LIVE PRICE FEED ===
function initPriceFeed() {
    console.log("🔌 Initializing Binance Feed...");
    const socket = new WebSocket('wss://stream.binance.com:9443/ws/eurusdt@ticker');

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // ticker uses 'c' for close price
        const price = parseFloat(data.c);
        if (!isNaN(price)) {
            livePrice = price;
            pHistory.push(price);
            if (pHistory.length > 50) pHistory.shift();
            updatePriceUI();
        }
    };

    socket.onclose = () => {
        console.warn("🔌 Price Feed Closed. Reconnecting in 5s...");
        setTimeout(initPriceFeed, 5000);
    };

    socket.onerror = (error) => {
        console.error("🔌 Pricing Feed Error:", error);
        socket.close();
    };
}

function updatePriceUI() {
    const priceEl = document.getElementById('price-main');
    if (!priceEl || !livePrice) return;
    priceEl.textContent = livePrice.toFixed(5);
    priceEl.style.color = livePrice > prevPrice ? 'var(--trade-up)' : (livePrice < prevPrice ? 'var(--trade-down)' : 'var(--text-primary)');

    // Update Active Signal View with livePrice
    if (currentActiveRecord) {
        displayActiveSignal(currentActiveRecord);
    }

    // Refresh history first page if needed
    if (activeTab === 'overview' && currentPage === 1) {
        renderHistoryPage();
    }

    // Sparkline
    const linePath = document.getElementById('spark-line');
    const fillPath = document.getElementById('spark-fill');
    if (linePath && fillPath && pHistory.length > 2) {
        const min = Math.min(...pHistory), max = Math.max(...pHistory);
        const range = (max - min) || 0.0001;
        const width = 100, height = 60;
        const points = pHistory.map((v, i) => {
            const x = (i / (pHistory.length - 1)) * width;
            const y = height - ((v - min) / range) * (height - 10) - 5;
            return { x, y };
        });
        const d = `M ${points.map(p => `${p.x} ${p.y}`).join(' L ')}`;
        linePath.setAttribute('d', d);
        const fillD = `${d} L ${points[points.length - 1].x} ${height} L ${points[0].x} ${height} Z`;
        fillPath.setAttribute('d', fillD);
    }
    prevPrice = livePrice;
}
