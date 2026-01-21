# AUTO v0 - Implementation Guide

## 🎯 Quick Start

### Prerequisites
- MPV Anchor verified and frozen (tag: `mpv-verified`)
- Backend API running and accessible
- Python 3.8+

### Running AUTO v0

```bash
# Single execution (manual trigger for testing)
python auto_executor.py

# Scheduled execution (cron/task scheduler)
# Run once per day at market open (e.g., 9:00 AM UTC)
```

---

## 📋 What AUTO v0 Does

AUTO v0 is a **proof of repeatability**. It:

1. ✅ Fetches the latest signal from the verified backend (read-only)
2. ✅ Validates signal integrity (timestamp, TTL, validity)
3. ✅ Enforces daily execution cap (max 1/day)
4. ✅ Executes to MT4 Demo (currently simulated)
5. ✅ Logs everything (append-only, immutable)

---

## 🚫 What AUTO v0 Does NOT Do

- ❌ Generate signals
- ❌ Modify signals
- ❌ Filter or optimize
- ❌ Retry failed executions
- ❌ Execute multiple times per day
- ❌ Make trading decisions

---

## 📂 File Structure

```
quantix-live-execution/
├── AUTO_V0_DEFINITION.md          # Formal definition
├── AUTO_V0_README.md               # This file
├── auto_executor.py                # Main execution adapter
├── auto_execution_log.jsonl        # Append-only execution log
├── daily_gate_log.jsonl            # Append-only gate decisions
└── MPV_VERIFIED_SNAPSHOT_20260121.md  # Anchor baseline
```

---

## 📊 Log Format

### Execution Log (`auto_execution_log.jsonl`)
Each line is a JSON object:
```json
{
  "signal_id": "live-003",
  "signal_time": "2026-01-21T05:58:10.807267+00:00",
  "auto_order_time": "2026-01-21T06:00:15.123456+00:00",
  "latency_ms": 125,
  "signal_price": 1.17165,
  "execution_price": 1.17165,
  "direction": "BUY",
  "tp": 1.17365,
  "sl": 1.17015,
  "confidence": 67,
  "status": "EXECUTED",
  "mt4_order_id": null,
  "execution_mode": "DEMO_SIMULATION"
}
```

### Daily Gate Log (`daily_gate_log.jsonl`)
```json
{
  "timestamp": "2026-01-21T06:00:00.000000+00:00",
  "signal_id": "live-003",
  "decision": "EXECUTE",
  "reason": "Signal valid, gate open, executing",
  "date": "2026-01-21"
}
```

---

## ✅ Success Criteria

AUTO v0 is considered **PASS** if:

1. ✅ Executes correct signal (matching signal_id from backend)
2. ✅ Never executes expired signals
3. ✅ Never executes more than 1 signal per day
4. ✅ Latency < 5000ms (configurable)
5. ✅ All logs are complete and auditable

AUTO v0 **FAILS** if:

1. ❌ Double execution on same day
2. ❌ Executes expired signal
3. ❌ Manual override after auto execution
4. ❌ Signal logic modified to "make auto work better"

---

## 🔧 Configuration

Edit `auto_executor.py` to configure:

```python
# API endpoint
API_BASE = "https://signalgeniusai-production.up.railway.app"

# Maximum acceptable latency
MAX_LATENCY_MS = 5000

# Log files (append-only)
EXECUTION_LOG_FILE = "auto_execution_log.jsonl"
DAILY_GATE_LOG_FILE = "daily_gate_log.jsonl"
```

---

## 🔄 Scheduling (Production)

### Windows Task Scheduler
```powershell
# Run daily at 9:00 AM UTC
schtasks /create /tn "Quantix AUTO v0" /tr "python D:\path\to\auto_executor.py" /sc daily /st 09:00
```

### Linux Cron
```bash
# Run daily at 9:00 AM UTC
0 9 * * * cd /path/to/quantix-live-execution && python auto_executor.py >> auto_v0.log 2>&1
```

---

## 📈 Monitoring

Check logs daily:

```bash
# View execution log
cat auto_execution_log.jsonl | jq .

# View gate decisions
cat daily_gate_log.jsonl | jq .

# Count executions today
grep "$(date -u +%Y-%m-%d)" auto_execution_log.jsonl | wc -l
```

---

## 🛑 Exit Condition

AUTO v0 phase ends when:

1. ✅ 10-20 successful executions logged
2. ✅ No constraint violations
3. ✅ Evidence bundle complete

After exit, you may proceed to:
- AUTO v1 (enhanced automation)
- Optimization phase
- Scale to live account

---

## ⚠️ Important Notes

1. **Read-only Anchor**: Never modify MPV baseline
2. **Append-only logs**: Never delete or edit log entries
3. **No manual override**: Once auto executes, hands off
4. **Simulation mode**: Current version simulates MT4 execution
5. **MT4 Integration**: Replace `execute_to_mt4_demo()` with actual MT4 API

---

## 🔗 Related Documents

- `AUTO_V0_DEFINITION.md` - Formal specification
- `MPV_VERIFIED_SNAPSHOT_20260121.md` - Anchor baseline
- `LIVE_PROOF_RULES.md` - Original MPV rules

---

## 📞 Support

For questions or issues:
1. Check logs first
2. Verify anchor baseline unchanged
3. Review AUTO v0 definition
4. Document any anomalies

**Remember**: AUTO v0 proves repeatability, not profitability.
