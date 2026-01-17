/**
 * Payload - Data Fetching and Orchestration
 */

import { renderCard } from "./signals.js";

const LATEST_API = "/api/v1/signal/latest";

function updateUI(data) {
    const root = document.getElementById("signal-card");
    if (!root) return;

    root.innerHTML = renderCard(data);
}

async function fetchLatestSignal() {
    try {
        const response = await fetch(LATEST_API);
        const data = await response.json();
        updateUI(data);
    } catch (err) {
        console.error("Fetch error:", err);
        updateUI(null);
    }
}

// Initial load
fetchLatestSignal();

// Auto-refresh every 15 seconds
setInterval(fetchLatestSignal, 15000);
