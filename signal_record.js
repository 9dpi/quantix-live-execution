import { getSignalStatus } from "./signals.js";

const LIVE_API_URL = "/signal/latest";

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
    document.getElementById('waiting-state').classList.add('hidden');
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
    document.getElementById('waiting-state').classList.add('hidden');
    document.getElementById('market-closed').classList.add('hidden');
    document.getElementById('signal-record').classList.remove('hidden');

    const isBuy = record.direction === 'BUY';
    document.getElementById('record-asset').textContent = record.asset || 'EUR/USD';

    const dirText = document.getElementById('dir-text');
    dirText.textContent = isBuy ? "🟢 BUY" : "🔴 SELL";
    dirText.className = isBuy ? "BUY" : "SELL";

    // Format Timestamp (100% Sync with T1 executed_at)
    const recordDate = new Date(record.executed_at || record.signal_time);
    const dateOptions = { day: 'numeric', month: 'short', year: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' };
    const dateStr = recordDate.toLocaleDateString('en-GB', dateOptions);
    const timeStr = recordDate.toLocaleTimeString('en-GB', timeOptions);

    document.getElementById('record-generated-at').innerText = `${dateStr} · ${timeStr} UTC`;

    // Smart Status based on age
    const statusInfo = getSignalStatus({
        timestamp: record.executed_at || record.signal_time,
        validity: 90
    });

    const statusEl = document.getElementById('record-main-status');
    const validityEl = document.getElementById('record-validity');

    if (statusInfo.isLive) {
        statusEl.innerText = "ACTIVE — currently verifying";
        statusEl.className = "meta-value-vertical status-text live";
        validityEl.innerText = 'ACTIVE';
        validityEl.className = 'text-green';
    } else {
        statusEl.innerText = "EXPIRED — no longer active";
        statusEl.className = "meta-value-vertical status-text expired";
        validityEl.innerText = 'EXPIRED';
        validityEl.className = 'text-red';
    }

    document.getElementById('record-entry').textContent = record.entry || record.execution_price || record.signal_price;
    document.getElementById('record-tp').textContent = record.tp;
    document.getElementById('record-sl').textContent = record.sl;
    document.getElementById('record-confidence').textContent = `${record.confidence}%`;
    document.getElementById('record-strategy').textContent = record.strategy || "Quantix AI Core [T1]";
    document.getElementById('record-volatility').textContent = "Verified";
}

function displayWaitingState() {
    document.getElementById('waiting-state').classList.remove('hidden');
    document.getElementById('signal-record').classList.add('hidden');
    document.getElementById('market-closed').classList.add('hidden');
}

async function initializeSignalRecord() {
    console.log("Initializing Signal Record Display...");

    // 1. Check Market Status
    if (!isMarketOpen()) {
        console.log("Market is closed. Showing closed state.");
        displayMarketClosed();
        return;
    }

    // 2. Fetch Logic
    const latestRecord = await fetchLatestSignalRecord();

    if (latestRecord) {
        const recordDate = new Date(latestRecord.executed_at || latestRecord.signal_time);
        const now = new Date();
        const daysDiff = (now - recordDate) / (1000 * 60 * 60 * 24);

        if (daysDiff <= 7) {
            displaySignalRecord(latestRecord);
        } else {
            console.log("Signal Record too old (> 7 days), showing waiting state");
            displayWaitingState();
        }
    } else {
        console.log("No Signal Record available, showing waiting state");
        displayWaitingState();
    }
}

document.addEventListener('DOMContentLoaded', initializeSignalRecord);
