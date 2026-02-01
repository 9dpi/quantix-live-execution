const LIVE_API_URL = "https://signalgeniusai-production.up.railway.app/signal/latest";
const SB_URL = "https://wttsaprezgvircanthbk.supabase.co/rest/v1/fx_signals";
const SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0dHNhcHJlemd2aXJjYW50aGJrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODM2ODA3MCwiZXhwIjoyMDgzOTQ0MDcwfQ.QGewz8bDfBC6vJce6g4-sHA164bL1y0u71d6HH7PYVk";

let activeTab = 'active';

// Tab Switching Logic
window.switchTab = (tab) => {
    activeTab = tab;

    // Update Button UI
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.innerText.toLowerCase().includes(tab)) btn.classList.add('active');
    });

    // Toggle Content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`${tab}-tab`).classList.add('active');

    if (tab === 'history') loadHistory();
};

// --- ACTIVE TAB LOGIC ---

function isMarketOpen() {
    const now = new Date();
    const day = now.getUTCDay(); // 0 is Sunday, 6 is Saturday
    const hour = now.getUTCHours();
    // Forex: Open Sun 22:00 UTC to Fri 22:00 UTC
    if (day === 6) return false;
    if (day === 5 && hour >= 22) return false;
    if (day === 0 && hour < 22) return false;
    return true;
}

async function fetchLatestSignal() {
    const recordEl = document.getElementById('signal-record');
    const closedEl = document.getElementById('market-closed');

    // Early local check
    if (!isMarketOpen()) {
        if (closedEl) closedEl.classList.remove('hidden');
        if (recordEl) recordEl.classList.add('hidden');
        return;
    }

    try {
        const response = await fetch(LIVE_API_URL);
        if (!response.ok) throw new Error("API Offline");
        const data = await response.json();

        if (data.status === "MARKET_CLOSED") {
            if (closedEl) closedEl.classList.remove('hidden');
            if (recordEl) recordEl.classList.add('hidden');
            return;
        }

        displayActiveSignal(data);
    } catch (error) {
        console.error("Fetch failed:", error);
        // If API fails during market hours, we might be awaiting a signal
        // We'll leave it in its current state or show a generic message
    }
}

function displayActiveSignal(record) {
    document.getElementById('market-closed').classList.add('hidden');
    document.getElementById('signal-record').classList.remove('hidden');

    // Header
    const ts = record.executed_at || record.timestamp;
    const dateObj = (ts && !isNaN(new Date(ts))) ? new Date(ts) : null;
    if (dateObj) {
        const dStr = dateObj.toLocaleDateString('en-CA');
        const tStr = dateObj.toLocaleTimeString('en-GB', { hour12: false, timeZone: 'UTC' });
        document.getElementById('record-generated-at').innerText = `${dStr} ${tStr} UTC`;
    }

    // Asset & Direction
    document.getElementById('record-asset').textContent = record.asset || 'EUR/USD';
    const dirText = document.getElementById('dir-text');
    const isBuy = (record.direction || "BUY") === 'BUY';
    dirText.textContent = isBuy ? "🟢 BUY" : "🔴 SELL";
    dirText.className = isBuy ? "BUY" : "SELL";

    document.getElementById('strength-text').textContent = `(${record.confidence || 0}%)`;

    // Levels
    const f = (val) => val ? parseFloat(val).toFixed(5) : "---";
    document.getElementById('record-entry').textContent = f(record.entry || record.entry_low);
    document.getElementById('record-tp').textContent = f(record.tp);
    document.getElementById('record-sl').textContent = f(record.sl);

    // Analysis
    document.getElementById('record-confidence').textContent = `${record.confidence || 0}%`;
    document.getElementById('record-strategy').textContent = record.strategy || "Quantix AI Core";

    // Status Mapping
    const statusEl = document.getElementById('record-status-detailed');
    const state = record.state || 'WAITING_FOR_ENTRY';

    let label = "Checking...";
    let color = "var(--text-secondary)";

    if (state === 'WAITING_FOR_ENTRY') { label = "⏳ PENDING (Waiting Entry)"; color = "var(--primary-blue)"; }
    else if (state === 'ENTRY_HIT') { label = "🚀 ACTIVE (Monitoring)"; color = "var(--accent-green)"; }
    else if (state === 'TP_HIT') { label = "🎯 SUCCESS (Target Hit)"; color = "var(--accent-green)"; }
    else if (state === 'SL_HIT') { label = "🛑 STOPPED (Exit Hit)"; color = "var(--accent-red)"; }
    else if (state === 'CANCELLED') { label = "⚪ NO TRADE (Expired)"; }

    statusEl.innerText = label;
    statusEl.style.color = color;
}

// --- HISTORY TAB LOGIC ---

async function loadHistory() {
    const tbody = document.getElementById('history-body');
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">⏳ Fetching History...</td></tr>';

    try {
        const asset = document.getElementById('filter-asset').value;
        const outcome = document.getElementById('filter-outcome').value;
        const sort = document.getElementById('filter-sort').value;

        // Construct Supabase PostgREST URL
        let url = `${SB_URL}?select=*&limit=100`;

        // Sorting
        const sortOrder = sort === 'asc' ? 'asc' : 'desc';
        url += `&order=generated_at.${sortOrder}`;

        // Asset filter
        if (asset !== 'ALL') {
            // Remove / if present to match DB format e.g. "EURUSD"
            const dbAsset = asset.replace('/', '');
            url += `&asset=eq.${dbAsset}`;
        }

        // Outcome filter
        if (outcome !== 'ALL') {
            const stateMap = {
                'PROFIT': 'TP_HIT',
                'LOSS': 'SL_HIT',
                'CANCELLED': 'CANCELLED',
                'PENDING': 'WAITING_FOR_ENTRY'
            };
            const mappedState = stateMap[outcome];
            if (mappedState) {
                if (outcome === 'PENDING') {
                    url += `&state=in.(WAITING_FOR_ENTRY,ENTRY_HIT)`;
                } else {
                    url += `&state=eq.${mappedState}`;
                }
            }
        }

        console.log('Fetching history from Supabase:', url);
        const res = await fetch(url, {
            headers: {
                "apikey": SB_KEY,
                "Authorization": `Bearer ${SB_KEY}`
            }
        });

        if (!res.ok) {
            throw new Error(`Supabase Error: ${res.status} ${res.statusText}`);
        }

        let signals = await res.json();

        tbody.innerHTML = "";

        if (!signals || signals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">No records found.</td></tr>';
            return;
        }

        signals.forEach(sig => {
            const dt = new Date(sig.generated_at);

            if (isNaN(dt.getTime())) {
                console.warn('Invalid date for signal:', sig);
                return;
            }

            const dStr = dt.toLocaleDateString('en-CA');
            const tStr = dt.toLocaleTimeString('en-GB', { hour12: false, timeZone: 'UTC' }).slice(0, 5);

            const mapping = mapState(sig.state);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="mono" style="font-size: 0.8rem">${dStr} ${tStr}</td>
                <td><b>${sig.asset || 'N/A'}</b></td>
                <td><span class="direction-tag tag-${(sig.direction || 'BUY').toLowerCase()}">${sig.direction || 'BUY'}</span></td>
                <td class="mono">${parseFloat(sig.entry_price || sig.entry_low || 0).toFixed(5)}</td>
                <td class="mono">${parseFloat(sig.sl || 0).toFixed(5)}</td>
                <td class="mono">${parseFloat(sig.tp || 0).toFixed(5)}</td>
                <td><span class="outcome-badge outcome-${mapping.class}">${mapping.label}</span></td>
            `;
            tbody.appendChild(row);
        });

    } catch (e) {
        console.error("History fetch error:", e);
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--accent-red)">⚠️ Error loading history: ${e.message}</td></tr>`;
    }
}

function mapState(state) {
    if (state === 'TP_HIT') return { label: 'Successful', class: 'tp' };
    if (state === 'SL_HIT') return { label: 'Not Successful', class: 'sl' };
    if (state === 'CANCELLED') return { label: 'No Trade', class: 'expired' };
    return { label: 'Pending', class: 'pending' };
}

// Initial Run
document.addEventListener('DOMContentLoaded', () => {
    fetchLatestSignal();

    // Filter listeners
    document.getElementById('filter-asset').addEventListener('change', loadHistory);
    document.getElementById('filter-outcome').addEventListener('change', loadHistory);
    document.getElementById('filter-sort').addEventListener('change', loadHistory);

    // Auto-refresh (60s)
    setInterval(() => {
        if (activeTab === 'active') fetchLatestSignal();
    }, 60000);
});
