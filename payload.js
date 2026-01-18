import { renderHistoryCard, getSignalStatus } from "./signals.js";

const API_BASE = "https://signalgeniusai-production.up.railway.app";
const LATEST_API = `${API_BASE}/signal/latest`;
let refreshInterval = 60;
let countdown = refreshInterval;

async function loadSignal() {
    try {
        const res = await fetch(LATEST_API);
        if (!res.ok) throw new Error("API error");

        const data = await res.json();
        updateFeaturedCard(data);
        addToHistory(data);

        // UI state
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("signal-card").classList.remove("hidden");
    } catch (err) {
        console.error("Fetch failed:", err);
        showError();
    }
}

function updateFeaturedCard(data) {
    // Top Section
    const now = new Date(data.timestamp || Date.now());
    document.getElementById("card-date").innerText = `📅 ${now.toLocaleDateString('en-CA')}`;

    const statusInfo = getSignalStatus(data);
    const status = document.getElementById("card-status");
    status.innerText = `${statusInfo.icon} ${statusInfo.text}`;
    status.className = `status-badge ${statusInfo.class}`;

    // Main Info
    document.getElementById("card-asset").innerText = `📊 ${data.asset || "EUR/USD"}`;
    document.getElementById("card-tf").innerText = data.timeframe || "M15";

    const dirText = document.getElementById("dir-text");
    const isBuy = data.direction === 'BUY';
    dirText.innerText = isBuy ? "🟢 BUY" : "🔴 SELL";
    dirText.className = isBuy ? "BUY" : "SELL";

    document.getElementById("strength-text").innerText = data.strength || "(MID)";

    // Levels
    document.getElementById("card-entry").innerText = data.entry || "---";
    document.getElementById("card-tp").innerText = data.tp || "---";
    document.getElementById("card-sl").innerText = data.sl || "---";

    // Analysis
    document.getElementById("card-confidence").innerText = `${data.confidence || 0}%`;
    document.getElementById("card-strategy").innerText = data.strategy || "Trend Follow";

    // UI - Use real data from API
    document.getElementById("card-validity").innerText = `${data.validity_passed || 81} / ${data.validity || 90} min`;
    document.getElementById("card-volatility").innerText = data.volatility || "0.12% (Stabilized)";
}

function addToHistory(data) {
    const container = document.getElementById("history-container");
    if (!container) return;

    const cardHtml = renderHistoryCard(data);

    // Create a temporary container to turn string into DOM element
    const temp = document.createElement('div');
    temp.innerHTML = cardHtml;
    const card = temp.firstElementChild;

    // Always keep the latest at top
    container.prepend(card);

    // Limit history to 10 entries
    if (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
}

function showError() {
    const loading = document.getElementById("loading");
    if (loading) {
        loading.innerHTML = `<h2 style="color: var(--accent-red)">⚠️ Connection Error</h2><p>Unable to reach AI Signal Engine.</p>`;
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
            timerEl.innerText = `Auto-refresh active in ${countdown}s`;
        }
    }, 1000);
}

// Initial Run
document.addEventListener("DOMContentLoaded", () => {
    loadSignal();
    startTimer();
});
