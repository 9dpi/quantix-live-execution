/**
 * Payload - Data Fetching and Orchestration
 * Single source of truth for signal data
 */

import { renderCard, renderTelegramMessage } from "./signals.js";

const API_URL = "https://signalgeniusai-production.up.railway.app/api/v1/signal/latest";

function updateUI(data) {
    const root = document.getElementById("signal-card");
    if (!root) return;

    // Render as HTML card for web
    root.innerHTML = renderCard(data);

    // Also log Telegram message to console (ready for bot)
    if (data && data.status === "ok") {
        console.log("📱 Telegram Preview:\n" + renderTelegramMessage(data));
    }
}

// Initial fetch
async function fetchLatestSignal() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        updateUI(data);
    } catch (err) {
        console.error("Fetch error:", err);
        updateUI(null);
    }
}

// Initial load
fetchLatestSignal();

// Auto-refresh every 30 seconds
setInterval(fetchLatestSignal, 30000);
