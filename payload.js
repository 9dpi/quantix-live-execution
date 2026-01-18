/**
 * Payload – Data Fetching and Orchestration
 * Production Card UI Version
 */

import { renderCard, renderStats } from "./signals.js";

const API_BASE = "https://signalgeniusai-production.up.railway.app";
const LATEST_API = `${API_BASE}/signal/latest`;

function updateUI(data) {
    const root = document.getElementById("signal-container");

    if (!root || !data) return;

    root.innerHTML = renderCard(data);
}

async function fetchLatestSignal() {
    try {
        const res = await fetch(LATEST_API);
        const data = await res.json();
        updateUI(data);
    } catch (err) {
        console.error("Fetch error:", err);
    }
}

// Initial load
fetchLatestSignal();

// Auto refresh (live tracker feel)
setInterval(fetchLatestSignal, 15000);
