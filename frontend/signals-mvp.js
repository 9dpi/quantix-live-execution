/**
 * Signal Genius AI - MVP Frontend (Enhanced)
 * Connects to Railway backend and displays professional signal card
 */

const API_URL = "https://signalgeniusai-production.up.railway.app/api/v1/signal/latest";

document.addEventListener("DOMContentLoaded", async () => {
  const el = document.getElementById("signal");

  if (!el) {
    console.error("Element with id 'signal' not found!");
    return;
  }

  // Show loading state
  el.innerHTML = `
    <div class="signal-card loading">
      <div style="text-align: center; padding: 40px;">
        <div style="font-size: 24px; margin-bottom: 12px;">⏳</div>
        <div>Loading signal data...</div>
      </div>
    </div>
  `;

  try {
    const res = await fetch(API_URL);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();

    // Use renderer to display signal card
    if (typeof displaySignal === 'function') {
      displaySignal(data, 'signal');
    } else {
      // Fallback to raw JSON if renderer not loaded
      el.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }

    console.log("✅ Signal data loaded:", data);

  } catch (e) {
    el.innerHTML = `
      <div class="error-box">
        <h3>⚠️ Connection Error</h3>
        <p>${e.message}</p>
        <p><small>Please check your internet connection and try again.</small></p>
      </div>
    `;
    console.error("❌ Error fetching signal:", e);
  }
});

// Auto-refresh every 30 seconds (optional)
setInterval(async () => {
  const el = document.getElementById("signal");
  if (!el) return;

  try {
    const res = await fetch(API_URL);
    if (!res.ok) return;

    const data = await res.json();

    if (typeof displaySignal === 'function') {
      displaySignal(data, 'signal');
    }

    console.log("🔄 Signal refreshed");

  } catch (e) {
    console.error("❌ Auto-refresh failed:", e);
  }
}, 30000); // 30 seconds
