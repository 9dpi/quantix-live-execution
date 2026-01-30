import { getSignalStatus } from "./signals.js";

const LIVE_API_URL = "https://signalgeniusai-production.up.railway.app/signal/latest";
const FALLBACK_LOG_API = "https://raw.githubusercontent.com/9dpi/quantix-live-execution/main/auto_execution_log.jsonl";

function isMarketOpen() {
    const now = new Date();
    const day = now.getUTCDay(); // 0 is Sunday, 6 is Saturday
    const hour = now.getUTCHours();

    // Forex market hours: Open Sunday 22:00 UTC to Friday 22:00 UTC
    if (day === 6) return false; // Saturday: Always closed
    if (day === 5 && hour >= 22) return false; // Friday after 22:00: Closed
    if (day === 0 && hour < 22) return false; // Sunday before 22:00: Closed

    return true;
}

function displayMarketClosed() {
    document.getElementById('signal-record').classList.add('hidden');
    document.getElementById('market-closed').classList.remove('hidden');
}

async function fetchLatestSignalRecord() {
    try {
        const response = await fetch(LIVE_API_URL);

        if (response.status === 404) {
            console.log("API: Awaiting Execution");
            return null;
        }

        if (!response.ok) throw new Error("API Error");
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch live signal:", error);
        return null;
    }
}

function displaySignalRecord(record) {
    document.getElementById('market-closed').classList.add('hidden');
    document.getElementById('signal-record').classList.remove('hidden');

    const isBuy = record.direction === 'BUY';
    document.getElementById('record-asset').textContent = record.asset || 'EUR/USD';

    const dirText = document.getElementById('dir-text');
    dirText.textContent = isBuy ? "🟢 BUY" : "🔴 SELL";
    dirText.className = isBuy ? "BUY" : "SELL";

    // Safe Date Parsing
    const ts = record.executed_at || record.signal_time || record.timestamp;
    const dateObj = (ts && !isNaN(new Date(ts))) ? new Date(ts) : null;

    if (dateObj) {
        // Format: 2026-01-29 14:05:00 UTC (User preference for clarity)
        const dateOptions = { year: 'numeric', month: '2-digit', day: '2-digit' };
        const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: 'UTC' };
        const dStr = dateObj.toLocaleDateString('en-CA', dateOptions); // en-CA gives YYYY-MM-DD
        const tStr = dateObj.toLocaleTimeString('en-GB', timeOptions);
        document.getElementById('record-generated-at').innerText = `${dStr} ${tStr} UTC`;
    } else {
        document.getElementById('record-generated-at').innerText = "— (Historical Record)";
    }

    // Smart Status based on age
    const statusInfo = getSignalStatus({
        timestamp: record.executed_at || record.signal_time,
        validity: 90
    });

    const statusEl = document.getElementById('record-status-detailed');

    if (statusEl) {
        if (statusInfo.isLive) {
            statusEl.innerText = "ACTIVE — Monitoring Market";
            statusEl.className = 'text-green';
        } else {
            statusEl.innerText = "EXPIRED (Entry not hit before expiry)";
            statusEl.className = 'text-red';
        }
    }

    document.getElementById('record-entry').textContent = record.entry || record.execution_price || record.signal_price;
    document.getElementById('record-tp').textContent = record.tp;
    document.getElementById('record-sl').textContent = record.sl;
    document.getElementById('record-confidence').textContent = `${record.confidence}%`;
    document.getElementById('record-strategy').textContent = record.strategy || "Quantix AI Core [T1]";
    document.getElementById('record-volatility').textContent = "Verified";
}



async function initializeSignalRecord() {
    console.log("Initializing Signal Record Display...");

    // 1. Check Market Status
    if (!isMarketOpen()) {
        console.log("Market is closed. Showing closed state.");
        displayMarketClosed();
        return;
    }

    // 2. Try Live API First
    let latestRecord = await fetchLatestSignalRecord();

    // 3. Fallback to GitHub Logs if Live API has no active signal
    if (!latestRecord) {
        console.log("No live signal, fetching last update from logs...");
        try {
            const cacheBuster = `?t=${Date.now()}`;
            const response = await fetch(FALLBACK_LOG_API + cacheBuster);
            if (response.ok) {
                const text = await response.text();
                const lines = text.trim().split('\n').filter(line => line.trim());
                if (lines.length > 0) {
                    latestRecord = JSON.parse(lines[lines.length - 1]);
                    latestRecord.strategy = latestRecord.strategy || "Quantix Core [Record]";
                }
            }
        } catch (e) {
            console.error("Log fallback failed:", e);
        }
    }

    // 4. Display the signal card (Never show waiting state anymore)
    if (latestRecord) {
        displaySignalRecord(latestRecord);
    } else {
        console.log("Truly no data found.");
        // We could show an error, but staying on blank card or loading is better than the mascot
    }
}

document.addEventListener('DOMContentLoaded', initializeSignalRecord);
