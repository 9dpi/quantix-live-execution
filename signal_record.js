const API_BASE = 'https://telesignal-production.up.railway.app';
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

    document.getElementById('modal-title').innerText = `${symbol} · ${timeframe} · TradingView Preview`;
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

    // Update Nav Links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (tab === 'logs' && (link.innerText.includes('Logs') || link.innerText.includes('System Logs'))) {
            link.classList.add('active');
        } else if (tab === 'overview' && link.innerText.includes('Overview')) {
            link.classList.add('active');
        }
    });

    // Toggle Content
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

const AI_CORE_API = 'https://quantixaicore-production.up.railway.app/api/v1';

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
        const res = await fetch(`${API_BASE}/api/signals`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();

        if (json.active) {
            displayActiveSignal(json.active);
        } else {
            if (recordEl) recordEl.style.display = 'none';
            if (closedEl) closedEl.style.display = 'none';
            if (scanningEl) scanningEl.style.display = 'flex';
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

    // Duration Logic
    const entryLimit = record.activation_limit_mins || 35;
    const maxTrade = record.max_monitoring_mins || 90;
    document.getElementById('record-entry-duration').textContent = `${entryLimit}m`;
    document.getElementById('record-max-duration').textContent = `${maxTrade}m`;
    document.getElementById('record-warning-time').textContent = maxTrade;

    document.getElementById('record-asset').textContent = asset;
    document.getElementById('record-tf').textContent = tf;

    const dirText = direction === 'BUY' ? '🟢 BUY' : '🔴 SELL';
    document.getElementById('record-direction-text').textContent = dirText;
    document.getElementById('record-direction-text').style.color = direction === 'BUY' ? 'var(--trade-up)' : 'var(--trade-down)';

    document.getElementById('record-entry').textContent = parseFloat(entry).toFixed(5);
    document.getElementById('record-tp').textContent = parseFloat(tp).toFixed(5);
    document.getElementById('record-sl').textContent = parseFloat(sl).toFixed(5);
    document.getElementById('record-confidence').textContent = `${conf}%`;

    // Status Badge Logic
    const state = (record.status || record.state || 'WAITING').toUpperCase();
    const statusBadge = document.getElementById('record-status-badge');

    if (state === 'WAITING' || state === 'WAITING_FOR_ENTRY' || state === 'PUBLISHED') {
        statusBadge.textContent = 'WAITING FOR ENTRY';
        statusBadge.style.color = 'var(--quantix-accent)';
    } else if (state === 'ACTIVE' || state === 'ENTRY_HIT') {
        statusBadge.textContent = 'LIVE TRADE';
        statusBadge.style.color = 'var(--trade-up)';
    } else {
        statusBadge.textContent = state.replace(/_/g, ' ');
        statusBadge.style.color = 'var(--text-secondary)';
    }
}

async function loadHistory() {
    const tbody = document.getElementById('history-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center">⏳ Fetching History...</td></tr>';

    try {
        const res = await fetch(`${API_BASE}/api/signals`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();

        if (!json.success) throw new Error(json.message);

        allHistory = json.history || [];
        allHistory.sort((a, b) => new Date(b.generated_at) - new Date(a.generated_at));
        currentPage = 1;
        renderHistoryPage();

    } catch (e) {
        console.error("History fetch error:", e);
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color:var(--trade-down)">⚠️ Error loading history</td></tr>`;
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

    pageData.forEach(sig => {
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

        const statusLabel = getStatusLabel(sig);
        const pips = getPipsInfo(sig);

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

function getStatusLabel(s) {
    if (!s) return '--';
    const status = (s.status || s.state || '').toUpperCase();
    const result = (s.result || '').toUpperCase();

    if (result === 'PROFIT' || status === 'CLOSED_TP') return 'TP Hit';
    if (result === 'LOSS' || status === 'CLOSED_SL') return 'SL Hit';
    if (status === 'CLOSED_TIMEOUT') return 'Timeout';
    if (status === 'EXPIRED') return 'Expired';
    if (status === 'ACTIVE' || status === 'ENTRY_HIT') return 'Live Trade';
    if (status === 'WAITING' || status === 'WAITING_FOR_ENTRY' || status === 'PUBLISHED') return 'Waiting...';
    return status.replace(/_/g, ' ');
}

function getPipsInfo(s) {
    const entry = parseFloat(s.entry_price || s.entry || 0);
    const tp = parseFloat(s.tp || s.take_profit || 0);
    const sl = parseFloat(s.sl || s.stop_loss || 0);
    const result = (s.result || '').toUpperCase();

    let dist = 0;
    let label = '--';
    let color = 'var(--text-secondary)';

    if (result === 'PROFIT') {
        dist = Math.abs(entry - tp);
        label = `+${Math.round(dist * 10000 * 10) / 10} pips`;
        color = 'var(--trade-up)';
    } else if (result === 'LOSS') {
        dist = -Math.abs(entry - sl);
        label = `${Math.round(dist * 10000 * 10) / 10} pips`;
        color = 'var(--trade-down)';
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
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);

        let res = await fetch(`${AI_CORE_API}/validation-logs?limit=50`, { signal: controller.signal });
        clearTimeout(timeoutId);

        const json = await res.json();
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

                let ts = new Date(log.created_at).toLocaleString();

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
        const res = await fetch(`${AI_CORE_API}/analysis-logs?limit=20`);
        const json = await res.json();

        if (json.success && json.data) {
            hbody.innerHTML = '';
            json.data.forEach(beat => {
                const tr = document.createElement('tr');
                const ts = new Date(beat.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
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
    }, 60000);

    initPriceFeed();
});

// === LIVE PRICE FEED ===
function initPriceFeed() {
    const socket = new WebSocket('wss://stream.binance.com:9443/ws/eurusdt@trade');
    socket.onmessage = (event) => {
        const trade = JSON.parse(event.data);
        const price = parseFloat(trade.p);
        livePrice = price;
        pHistory.push(price);
        if (pHistory.length > 50) pHistory.shift();
        updatePriceUI();
    };
    socket.onerror = (error) => { console.warn("Pricing Feed Error:", error); };
}

function updatePriceUI() {
    const priceEl = document.getElementById('price-main');
    if (!priceEl || !livePrice) return;
    priceEl.textContent = livePrice.toFixed(5);
    priceEl.style.color = livePrice > prevPrice ? 'var(--trade-up)' : (livePrice < prevPrice ? 'var(--trade-down)' : 'var(--text-primary)');

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
