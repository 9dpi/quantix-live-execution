/**
 * Payload - Data Fetching and Rendering
 * Single source of truth for signal data
 */

const API_URL = "https://signalgeniusai-production.up.railway.app/api/v1/signal/latest";

function renderCard(data) {
    document.getElementById("signal-card").innerText =
        renderTelegramMessage(data);
}

// Initial fetch
fetch(API_URL)
    .then(res => res.json())
    .then(data => renderCard(data))
    .catch(() => {
        document.getElementById("signal-card").innerText =
            "⚠️ Failed to load signal";
    });

// Auto-refresh every 30 seconds
setInterval(() => {
    fetch(API_URL)
        .then(res => res.json())
        .then(data => renderCard(data))
        .catch(() => {
            // Silent fail on auto-refresh
        });
}, 30000);
