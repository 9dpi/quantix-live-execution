"""
AUTO v0 Scheduler with Guardrails
Polling mechanism: Every 60 seconds
Execution gate: Max 1/day (enforced by auto_executor.py)
"""

import os
import time
import json
from datetime import datetime, timezone
from auto_executor import run_auto_v0

# Guardrail 1: Kill Switch
AUTO_V0_ENABLED = os.getenv("AUTO_V0_ENABLED", "true").lower() == "true"

# Configuration
POLL_INTERVAL_SECONDS = 60  # Poll every 60 seconds
DAILY_SUMMARY_FILE = "daily_summary_log.jsonl"


def log_daily_summary():
    """
    Generate daily summary from execution and gate logs
    Called at end of day or on demand
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Count executions
    executions = 0
    if os.path.exists("auto_execution_log.jsonl"):
        with open("auto_execution_log.jsonl", 'r') as f:
            for line in f:
                if line.strip():
                    log = json.loads(line)
                    exec_time = datetime.fromisoformat(log['auto_order_time'].replace('Z', '+00:00'))
                    if exec_time.strftime("%Y-%m-%d") == today:
                        executions += 1
    
    # Count gate decisions
    signals_seen = 0
    skipped = 0
    if os.path.exists("daily_gate_log.jsonl"):
        with open("daily_gate_log.jsonl", 'r') as f:
            for line in f:
                if line.strip():
                    log = json.loads(line)
                    if log.get('date') == today:
                        if log['decision'] == 'EXECUTE':
                            signals_seen += 1
                        elif log['decision'] == 'SKIP':
                            skipped += 1
                            if log.get('signal_id') != 'N/A':
                                signals_seen += 1
    
    # Check for violations (should always be 0 for AUTO v0)
    violations = 0
    if executions > 1:
        violations += 1  # Violated 1/day constraint
    
    summary = {
        "date": today,
        "signals_seen": signals_seen,
        "executions": executions,
        "skipped": skipped,
        "violations": violations,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Append to daily summary log
    with open(DAILY_SUMMARY_FILE, 'a') as f:
        f.write(json.dumps(summary) + '\n')
    
    print(f"📊 Daily Summary: {summary}")
    return summary


def check_kill_switch():
    """Guardrail 2: Check kill switch before each cycle"""
    enabled = os.getenv("AUTO_V0_ENABLED", "true").lower() == "true"
    if not enabled:
        print("🛑 AUTO v0 DISABLED via kill switch (AUTO_V0_ENABLED=false)")
        return False
    return True


def scheduler_loop():
    """
    Main scheduler loop
    Polls every POLL_INTERVAL_SECONDS
    Gate enforcement happens inside auto_executor
    """
    # Guardrail: Check data feed configuration
    if not os.getenv("TWELVE_DATA_API_KEY"):
        raise RuntimeError(
            "❌ DATA FEED NOT CONFIGURED\n"
            "TWELVE_DATA_API_KEY environment variable is required.\n"
            "Scheduler aborted to prevent silent failures."
        )
    
    print("=" * 60)
    print("AUTO v0 Scheduler Started")
    print(f"Poll Interval: {POLL_INTERVAL_SECONDS}s")
    print(f"Kill Switch: AUTO_V0_ENABLED={AUTO_V0_ENABLED}")
    print(f"Data Feed: Twelve Data API configured ✓")
    print("=" * 60)
    
    cycle_count = 0
    last_summary_date = None
    
    while True:
        try:
            # Guardrail 2: Check kill switch
            if not check_kill_switch():
                print("⏸️ Scheduler paused. Set AUTO_V0_ENABLED=true to resume.")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue
            
            cycle_count += 1
            print(f"\n🔄 Cycle #{cycle_count} - {datetime.now(timezone.utc).isoformat()}")
            
            # Run AUTO v0 execution cycle
            # Gate enforcement (1/day) happens inside run_auto_v0()
            run_auto_v0()
            
            # Guardrail 3: Daily summary (once per day)
            current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if current_date != last_summary_date:
                log_daily_summary()
                last_summary_date = current_date
            
            # Wait for next poll
            print(f"⏳ Next poll in {POLL_INTERVAL_SECONDS}s...")
            time.sleep(POLL_INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped by user (Ctrl+C)")
            # Final summary before exit
            log_daily_summary()
            break
            
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
            print(f"⏳ Retrying in {POLL_INTERVAL_SECONDS}s...")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    # Guardrail 1: Check kill switch at startup
    if not AUTO_V0_ENABLED:
        print("🛑 AUTO v0 is DISABLED")
        print("Set environment variable: AUTO_V0_ENABLED=true to enable")
        exit(0)
    
    # Start scheduler
    scheduler_loop()
