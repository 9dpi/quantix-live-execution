# Signal Record Model - Workflow & UI Specification

## 📋 Document Purpose
This document defines the **Signal Record Model** - a transparent, non-commercial approach to displaying historical signal data without becoming a "signal selling" product.

---

## I. WORKFLOW (END-TO-END)

### 1️⃣ Default State: NO SIGNAL

**Conditions:**
- No signal generated today
- OR previous signal is EXPIRED/EXECUTED and no new signal exists

**System Behavior:**
- ❌ No price displayed
- ❌ No direction displayed  
- ❌ No results displayed

**UI Display:**
→ **Waiting State**

---

### 2️⃣ Signal Generated (LIVE - NOT shown to public)

**Conditions:**
- Backend generates signal
- Signal is LOCKED + ACTIVE
- Has TTL (Time To Live)

**System Behavior:**
Signal is:
- ✅ Sent to AUTO execution
- ✅ Logged internally
- ❌ **NOT displayed publicly as "live signal"**

> **🔑 Critical Point:**  
> **Live Signal ≠ Public Signal**

---

### 3️⃣ Signal Lifecycle Ends

Signal transitions to one of two states:
1. **EXECUTED** (auto/manual order placed)
2. **EXPIRED** (TTL expired, no order placed)

At this point, signal becomes:
✅ **Signal Record**

---

### 4️⃣ UI Update: SHOW SIGNAL RECORD (Latest Only)

**Rules:**
- ✅ Show only 1 Signal Record (most recent)
- ✅ Read-only
- ❌ No live updates
- ❌ No animations
- ❌ No CTA (Call To Action)

> **User Experience:**  
> When users visit the site, they see "something" - but it's history, not advice.

---

### 5️⃣ When New Signal Record Appears

- Old Signal Record is **replaced**
- ❌ No public archive
- ❌ No cherry-picking

---

## II. UI COPY (Production-Ready English)

### 🟢 STATE 1: WAITING (Default)

```
System Status: Waiting by Design

This system trades very rarely.

A signal will only appear when:
• Market conditions are exceptionally clear
• The confidence is the highest for the day
• No trade has been executed today

If nothing is shown, it means the system has decided not to trade.

No signal is not a problem. It is a decision.
```

---

### 🟡 STATE 2: SIGNAL RECORD (Latest)

```
Signal Record (Latest)
Read-only historical snapshot

Instrument: EURUSD
Direction: BUY
Reference Price: 1.17163
Generated At: 21 Jan 2026 · 06:09 UTC
Status: EXPIRED — no longer active

⚠️ Important Note

This signal is displayed for transparency only.
It shows what the system generated at a specific point in time.

The signal is no longer valid for execution.
Any decision to use this information is entirely the viewer's own responsibility.

📖 How to read this
• This is not a live trading instruction
• It is a historical record, not a recommendation
• Signals are generated before outcomes, never after

System Context:
Only the most recent Signal Record is shown to avoid cherry-picking and hindsight bias.
```

**Footer (small text):**
```
Long periods with no signals are intentional.
```

---

## III. GOLDEN RULES (Lock These 5 Rules)

| Rule | Description |
|------|-------------|
| ❌ **Never show ACTIVE signals publicly** | Only internal/AUTO execution sees live signals |
| ✅ **Only show Signal Records** | After signal becomes EXPIRED/EXECUTED |
| ⏱️ **Timestamp > Price** | Time of generation is more important than price level |
| 🚫 **No CTA** | No "trade now", no "follow", no action buttons |
| 🧠 **Explain meaning, not method** | UI explains what it is, not how to trade it |

---

## IV. STAKEHOLDER STATEMENT

**For Irfan / Non-Technical Stakeholders:**

> *"When you see nothing, the system is waiting.*  
> *When you see a Signal Record, you're looking at proof — not a suggestion."*

---

## V. TECHNICAL IMPLEMENTATION

### Data Source
- **NOT** from live API (`/signal/latest`)
- **FROM** append-only execution logs (GitHub public repo)
- Read-only, historical data only

### Display Logic
```javascript
// Fetch latest execution from logs
const latestRecord = await fetchFromGitHub('auto_execution_log.jsonl');

// Only show if within last 7 days
if (daysSinceGeneration <= 7) {
  displaySignalRecord(latestRecord);
} else {
  displayWaitingState();
}
```

### Status Mapping
| Internal Status | Public Display |
|----------------|----------------|
| EXECUTED | EXPIRED |
| EXPIRED | EXPIRED |
| ACTIVE | ❌ Never shown |

---

## VI. BENEFITS OF THIS MODEL

### ✅ Maintains Anchor Integrity
- No live signal selling
- No commercial pressure
- Pure transparency

### ✅ Solves UX "Empty State"
- Users see something meaningful
- Understand system is deliberate, not broken

### ✅ Legal/Compliance Safe
- Historical data only
- Clear disclaimers
- No trading advice

### ✅ No-Tech Friendly
- Simple language
- Clear expectations
- Honest communication

---

## VII. WHAT NOT TO DO

### ❌ DO NOT:
1. Add "win rate" or "performance"
2. Add "subscribe for signals"
3. Add real-time updates
4. Show multiple signals (archive)
5. Add outcome tracking (TP/SL hit)
6. Add "confidence score" as selling point
7. Add countdown timers
8. Add social proof ("X traders following")

---

## VIII. CONCLUSION

This workflow:
- ✅ Preserves Anchor integrity
- ✅ Solves UX concerns
- ✅ Avoids signal product trap
- ✅ Maintains discipline
- ✅ Suitable for non-technical audience

**Core Philosophy:**
> *Signal Records are proof of process, not promises of profit.*

---

## IX. FILES CREATED

1. `index_signal_record.html` - UI implementation
2. `signal_record.js` - Display logic
3. `SIGNAL_RECORD_WORKFLOW.md` - This document

**Status:** ✅ Ready for deployment  
**Anchor Compliance:** ✅ Fully compliant  
**AUTO v0 Impact:** ✅ No interference
