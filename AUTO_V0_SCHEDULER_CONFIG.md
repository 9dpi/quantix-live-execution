# AUTO v0 Scheduler Configuration

## 🎯 Purpose
Automated polling mechanism for AUTO v0 execution.  
**NOT** a decision-maker, just a timer that calls `auto_executor.py`.

---

## ⚙️ Configuration

### Poll Interval
```python
POLL_INTERVAL_SECONDS = 60  # Poll every 60 seconds
```

**Why 60 seconds, not "once per day"?**
- Gate enforcement (1/day) happens inside `auto_executor.py`
- Scheduler is just a polling mechanism
- Frequent polling ensures we catch signals quickly

---

## 🛡️ Guardrails (Mandatory)

### Guardrail 1: Kill Switch
```bash
# Enable AUTO v0
export AUTO_V0_ENABLED=true

# Disable AUTO v0 (emergency stop)
export AUTO_V0_ENABLED=false
```

**When to use:**
- ❌ Unexpected behavior detected
- ❌ Market anomaly
- ❌ Need to pause for maintenance

### Guardrail 2: Read-Only Environment
Scheduler **cannot**:
- ❌ Modify config at runtime
- ❌ Accept manual input
- ❌ Override gate decisions

### Guardrail 3: Daily Summary Log
Auto-generated at end of each day:

```json
{
  "date": "2026-01-21",
  "signals_seen": 1,
  "executions": 1,
  "skipped": 2,
  "violations": 0,
  "timestamp": "2026-01-21T23:59:59.000000+00:00"
}
```

**Violations** should **always be 0** for AUTO v0.

---

## 🚀 Running the Scheduler

### Manual Start (for testing)
```bash
# Windows
set AUTO_V0_ENABLED=true
python auto_scheduler.py

# Linux/Mac
export AUTO_V0_ENABLED=true
python auto_scheduler.py
```

### Background Service (production)

#### Windows (Task Scheduler)
```powershell
# Create scheduled task to run at startup
schtasks /create /tn "Quantix AUTO v0 Scheduler" /tr "python D:\Automator_Prj\Quantix_MPV\quantix-live-execution\auto_scheduler.py" /sc onstart /ru SYSTEM
```

#### Linux (systemd)
```bash
# Create service file: /etc/systemd/system/quantix-auto-v0.service
[Unit]
Description=Quantix AUTO v0 Scheduler
After=network.target

[Service]
Type=simple
User=quantix
WorkingDirectory=/path/to/quantix-live-execution
Environment="AUTO_V0_ENABLED=true"
ExecStart=/usr/bin/python3 auto_scheduler.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable quantix-auto-v0
sudo systemctl start quantix-auto-v0
```

---

## 📊 Monitoring

### Check if scheduler is running
```bash
# Windows
tasklist | findstr python

# Linux
ps aux | grep auto_scheduler
```

### View logs in real-time
```bash
# Execution log
tail -f auto_execution_log.jsonl

# Gate decisions
tail -f daily_gate_log.jsonl

# Daily summaries
tail -f daily_summary_log.jsonl
```

### Check daily summary
```bash
# View today's summary
cat daily_summary_log.jsonl | jq 'select(.date == "'$(date -u +%Y-%m-%d)'")'

# Check for violations
cat daily_summary_log.jsonl | jq 'select(.violations > 0)'
```

---

## 🛑 Emergency Stop

### Method 1: Kill Switch (recommended)
```bash
# Windows
set AUTO_V0_ENABLED=false

# Linux/Mac
export AUTO_V0_ENABLED=false
```

Scheduler will pause on next cycle (within 60 seconds).

### Method 2: Stop Process
```bash
# Windows
taskkill /F /IM python.exe /FI "WINDOWTITLE eq auto_scheduler*"

# Linux
pkill -f auto_scheduler.py
```

---

## ⚠️ What NOT to Do

### ❌ DO NOT:
1. **Change poll interval to "once per day"**  
   → Gate handles 1/day, scheduler is just polling
   
2. **Add retry logic**  
   → AUTO v0 is proof of repeatability, not reliability
   
3. **Add manual override**  
   → Violates read-only constraint
   
4. **Modify signal logic to "make it work better"**  
   → AUTO v0 proves MPV works, not that we can improve it

---

## 📈 Success Metrics

After 10-20 days, check:

```bash
# Total executions
cat auto_execution_log.jsonl | wc -l

# Total violations (should be 0)
cat daily_summary_log.jsonl | jq '.violations' | awk '{sum+=$1} END {print sum}'

# Average signals per day
cat daily_summary_log.jsonl | jq '.signals_seen' | awk '{sum+=$1; count++} END {print sum/count}'
```

---

## 🔄 Next Steps

1. ✅ Setup scheduler with guardrails
2. ⏳ Run for 10-20 executions
3. 📦 Build AUTO v0 Evidence Bundle
4. 🧾 Freeze AUTO v0
5. 👉 Then discuss AUTO v1 / MT4 integration

---

## 📞 Troubleshooting

### Scheduler not executing
- Check kill switch: `echo $AUTO_V0_ENABLED`
- Check daily gate: `cat daily_gate_log.jsonl | tail -1`
- Check backend API: `curl https://signalgeniusai-production.up.railway.app/health`

### Multiple executions per day
- **VIOLATION!** This should never happen
- Check `daily_summary_log.jsonl` for violations
- Review `auto_execution_log.jsonl` for duplicate entries
- Stop scheduler immediately and investigate

### No executions for several days
- Check if signals are being generated (backend)
- Check gate log for SKIP reasons
- Verify market hours (forex closed on weekends)

---

## 🔗 Related Files

- `auto_executor.py` - Core execution logic
- `AUTO_V0_DEFINITION.md` - Formal specification
- `AUTO_V0_README.md` - Implementation guide

---

**Remember**: Scheduler is a **polling mechanism**, not a decision-maker.  
All constraints are enforced by `auto_executor.py`.
