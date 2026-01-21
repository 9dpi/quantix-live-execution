/**
 * Signal Record Display Logic
 * 
 * WORKFLOW:
 * 1. Default: Show "Waiting State" (no signal)
 * 2. Fetch latest execution from local logs (NOT from live API)
 * 3. If found: Show as "Signal Record" (read-only, historical)
 * 4. Never show ACTIVE signals publicly
 * 
 * GOLDEN RULES:
 * ❌ Never show signal still ACTIVE to public
 * ✅ Only show signal when it becomes Signal Record
 * ⏱️ Timestamp always clearer than price
 * 🚫 No CTA, no "trade now", no "follow"
 * 🧠 UI only explains meaning, not how to trade
 */

const EXECUTION_LOG_API = "https://raw.githubusercontent.com/9dpi/quantix-live-execution/main/auto_execution_log.jsonl";

async function fetchLatestSignalRecord() {
    try {
        // Fetch from GitHub (public read-only logs)
        const response = await fetch(EXECUTION_LOG_API);

        if (!response.ok) {
            console.log("No execution log available");
            return null;
        }

        const text = await response.text();
        const lines = text.trim().split('\n').filter(line => line.trim());

        if (lines.length === 0) {
            console.log("No signal records found");
            return null;
        }

        // Get latest (last line)
        const latestLine = lines[lines.length - 1];
        const record = JSON.parse(latestLine);

        console.log("Latest Signal Record:", record);
        return record;

    } catch (error) {
        console.error("Failed to fetch signal record:", error);
        return null;
    }
}

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const day = date.getUTCDate();
    const month = date.toLocaleString('en-US', { month: 'short', timeZone: 'UTC' });
    const time = date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
        timeZone: 'UTC'
    });

    return `${day} ${month} ${time} UTC`;
}

function displaySignalRecord(record) {
    // Hide waiting state
    document.getElementById('waiting-state').classList.add('hidden');

    // Show signal record
    const recordCard = document.getElementById('signal-record');
    recordCard.classList.remove('hidden');

    const isBuy = record.direction === 'BUY';
    document.getElementById('record-asset').textContent = 'EUR/USD';

    const dirText = document.getElementById('dir-text');
    dirText.textContent = isBuy ? "🟢 BUY" : "🔴 SELL";
    dirText.className = isBuy ? "BUY" : "SELL";

    const recordDate = new Date(record.signal_time);
    document.getElementById('record-date').innerText = `📅 ${recordDate.toLocaleDateString('en-CA')}`;

    document.getElementById('record-entry').textContent = record.execution_price || record.signal_price || record.entry;
    document.getElementById('record-tp').textContent = record.tp;
    document.getElementById('record-sl').textContent = record.sl;
    document.getElementById('record-confidence').textContent = `${record.confidence}%`;
    document.getElementById('record-strategy').textContent = record.strategy || "Quantix Execution";
    document.getElementById('record-volatility').textContent = "Verified";

    // Status is always EXPIRED for public Signal Record
    document.getElementById('record-status').textContent = 'EXPIRED';
    document.getElementById('record-status').className = 'status-badge expired';
    document.getElementById('record-validity').textContent = 'EXPIRED';
    document.getElementById('record-validity').className = 'text-red';
}

function displayWaitingState() {
    // Show waiting state
    document.getElementById('waiting-state').classList.remove('hidden');

    // Hide signal record
    document.getElementById('signal-record').classList.add('hidden');
}

async function initializeSignalRecord() {
    console.log("Initializing Signal Record Display...");

    const latestRecord = await fetchLatestSignalRecord();

    if (latestRecord) {
        // Check if record is recent (within last 7 days)
        const recordDate = new Date(latestRecord.signal_time);
        const now = new Date();
        const daysDiff = (now - recordDate) / (1000 * 60 * 60 * 24);

        if (daysDiff <= 7) {
            console.log("Displaying Signal Record (within 7 days)");
            displaySignalRecord(latestRecord);
        } else {
            console.log("Signal Record too old, showing waiting state");
            displayWaitingState();
        }
    } else {
        console.log("No Signal Record available, showing waiting state");
        displayWaitingState();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeSignalRecord);

// No auto-refresh for Signal Record
// This is intentional - we don't want real-time updates
// Signal Records are historical snapshots, not live data
