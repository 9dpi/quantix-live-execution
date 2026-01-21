import { getSignalStatus } from "./signals.js";

const API_BASE = "https://signalgeniusai-production.up.railway.app";
const LATEST_API = `${API_BASE}/signal/latest`;
let refreshInterval = 30; // Faster sync for live mode
let countdown = refreshInterval;

async function loadSignal() {
    try {
        const res = await fetch(LATEST_API);
        if (res.status === 404) {
            document.getElementById("loading").innerHTML = `
                <div class="waiting-state">
                    <div class="waiting-icon">⟳</div>
                    <h2 class="sub-header" style="color: var(--primary-cyan); font-size: 1.5rem;">Awaiting Command</h2>
                    <p class="waiting-description" style="color: var(--text-dim); font-size: 0.9rem;">The system is ready for manual execution trigger.</p>
                </div>`;
            return;
        }
        if (res.status === 403) {
            document.getElementById("loading").innerHTML = `
                <div class="waiting-state">
                    <div class="waiting-icon" style="color: var(--accent-red)">⚠</div>
                    <h2 class="sub-header" style="color: var(--accent-red); font-size: 1.5rem;">Market Closed</h2>
                    <p class="waiting-description" style="color: var(--text-dim); font-size: 0.9rem;">Execution blocked. Protocols offline.</p>
                </div>`;
            return;
        }
        if (!res.ok) throw new Error("API error");

        const data = await res.json();
        updateFeaturedCard(data);

        // UI state
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("signal-card").classList.remove("hidden");
    } catch (err) {
        console.error("Fetch failed:", err);
        showError();
    }
}

function updateFeaturedCard(data) {
    const timestamp = data.executed_at || data.timestamp || Date.now();
    const now = new Date(timestamp);
    document.getElementById("card-date").innerText = `DATE: ${now.toLocaleDateString('en-CA').replace(/-/g, '.')}`;

    if (data.signal_id) {
        document.getElementById("card-id").innerText = data.signal_id.toUpperCase();
    }

    const statusInfo = getSignalStatus(data);
    const status = document.getElementById("card-status");
    status.innerText = (data.status || "EXECUTED").toUpperCase();
    status.className = `status-badge ${statusInfo.class}`;

    document.getElementById("card-asset").innerText = data.asset;
    document.getElementById("card-tf").innerText = "SYSTEM_M15";

    const dirText = document.getElementById("dir-text");
    const isBuy = data.direction === 'BUY';
    dirText.innerText = isBuy ? "BUY" : "SELL";
    dirText.className = isBuy ? "BUY" : "SELL";

    document.getElementById("strength-text").innerText = data.mode === "LIVE" ? "PROTOCOL_LIVE" : "PROTOCOL_SIM";

    document.getElementById("card-entry").innerText = parseFloat(data.entry).toFixed(5);
    document.getElementById("card-tp").innerText = parseFloat(data.tp).toFixed(5);
    document.getElementById("card-sl").innerText = parseFloat(data.sl).toFixed(5);
    document.getElementById("card-confidence").innerText = `${data.confidence}%`;
    document.getElementById("card-strategy").innerText = "NEURAL_FLW";
    document.getElementById("card-validity").innerText = `ACTIVE`;
    document.getElementById("card-volatility").innerText = "VERIFIED";
}

function showError() {
    const loading = document.getElementById("loading");
    if (loading) {
        loading.innerHTML = `
            <div class="waiting-state">
                <div class="waiting-icon" style="color: var(--accent-red)">✖</div>
                <h2 class="sub-header" style="color: var(--accent-red); font-size: 1.5rem;">Link Error</h2>
                <p class="waiting-description" style="color: var(--text-dim); font-size: 0.9rem;">Protocol sync failed. Check terminal.</p>
            </div>`;
    }
}

function startTimer() {
    setInterval(() => {
        countdown--;
        if (countdown <= 0) {
            countdown = refreshInterval;
            loadSignal();
        }
        const timerEl = document.getElementById("refresh-indicator");
        if (timerEl) {
            timerEl.innerText = `SYNCING_PROTOCOL... (${countdown}S)`;
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    loadSignal();
    startTimer();
});
