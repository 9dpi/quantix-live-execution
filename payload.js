import { getSignalStatus } from "./signals.js";

const API_BASE = "https://signalgeniusai-production.up.railway.app";
const LATEST_API = `${API_BASE}/signal/latest`;
let refreshInterval = 60;
let countdown = refreshInterval;

async function loadSignal() {
    try {
        const res = await fetch(LATEST_API);
        if (res.status === 404) {
            document.getElementById("loading").innerHTML = `<h2>⏳ Awaiting Execution</h2><p>Wait for manual signal trigger.</p>`;
            return;
        }
        if (res.status === 403) {
            document.getElementById("loading").innerHTML = `<h2 style="color: var(--accent-red)">🚫 Market Closed</h2><p>Execution blocked until market opens.</p>`;
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
    document.getElementById("card-date").innerText = `📅 ${now.toLocaleDateString('en-CA')}`;

    const statusInfo = getSignalStatus(data);
    const status = document.getElementById("card-status");
    status.innerText = data.status || "EXECUTED";
    status.className = `status-badge ${statusInfo.class}`;

    document.getElementById("card-asset").innerText = `📊 ${data.asset}`;
    document.getElementById("card-tf").innerText = "M15";

    const dirText = document.getElementById("dir-text");
    const isBuy = data.direction === 'BUY';
    dirText.innerText = isBuy ? "🟢 BUY" : "🔴 SELL";
    dirText.className = isBuy ? "BUY" : "SELL";

    document.getElementById("strength-text").innerText = data.mode === "LIVE" ? "⚡ LIVE" : "SIM";

    document.getElementById("card-entry").innerText = data.entry;
    document.getElementById("card-tp").innerText = data.tp;
    document.getElementById("card-sl").innerText = data.sl;
    document.getElementById("card-confidence").innerText = `${data.confidence}%`;
    document.getElementById("card-strategy").innerText = "Quantix Execution";
    document.getElementById("card-validity").innerText = `ACTIVE`;
    document.getElementById("card-volatility").innerText = "Real-time Verified";
}

function showError() {
    const loading = document.getElementById("loading");
    if (loading) {
        loading.innerHTML = `<h2 style="color: var(--accent-red)">⚠️ Connection Error</h2>`;
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
            timerEl.innerText = `Syncing... (${countdown}s)`;
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    loadSignal();
    startTimer();
});
