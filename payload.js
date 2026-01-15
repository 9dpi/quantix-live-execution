/**
 * Payload - Data Fetching and Orchestration
 * Single source of truth for signal data
 */

const API_URL = "https://signalgeniusai-production.up.railway.app/api/v1/signal/latest";

function updateUI(data) {
    const root = document.getElementById("signal-root");
    if (!root) return;

    // Render as HTML card for web
    root.innerHTML = renderSignalHTML(data);

    // Also log Telegram message to console (ready for bot)
    console.log("📱 Telegram Preview:\n" + renderTelegramMessage(data));
}

// Initial fetch
fetch(API_URL)
    .then(res => res.json())
    .then(data => updateUI(data))
    .catch((err) => {
        console.error("Fetch error:", err);
        updateUI(null);
    });

// Auto-refresh every 30 seconds
setInterval(() => {
    fetch(API_URL)
        .then(res => res.json())
        .then(data => updateUI(data))
        .catch(() => {
            // Silent fail on auto-refresh
        });
}, 30000);
