"""
AUTO v0 Execution Adapter
Built on: MPV Anchor (read-only)
Purpose: Prove repeatability without altering signal validity

CONSTRAINTS:
- Max 1 execution per day
- Read-only signal consumption
- Append-only logging
- No signal modification
- No retry logic
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

# Configuration
API_BASE = os.getenv("API_BASE", "https://signalgeniusai-production.up.railway.app")
EXECUTION_LOG_FILE = "auto_execution_log.jsonl"  # Append-only
DAILY_GATE_LOG_FILE = "daily_gate_log.jsonl"    # Append-only
MAX_LATENCY_MS = 5000  # Maximum acceptable latency

class DailyExecutionGate:
    """Enforces 1 execution per day constraint"""
    
    @staticmethod
    def get_today_date() -> str:
        """Get current date in UTC"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    @staticmethod
    def has_executed_today() -> bool:
        """Check if we've already executed today"""
        if not os.path.exists(EXECUTION_LOG_FILE):
            return False
        
        today = DailyExecutionGate.get_today_date()
        
        try:
            with open(EXECUTION_LOG_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        log_entry = json.loads(line)
                        exec_time = datetime.fromisoformat(log_entry['auto_order_time'].replace('Z', '+00:00'))
                        if exec_time.strftime("%Y-%m-%d") == today:
                            return True
        except Exception as e:
            print(f"⚠️ Error checking daily gate: {e}")
        
        return False
    
    @staticmethod
    def log_gate_decision(signal_id: str, decision: str, reason: str):
        """Log daily gate decision (append-only)"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signal_id": signal_id,
            "decision": decision,  # EXECUTE or SKIP
            "reason": reason,
            "date": DailyExecutionGate.get_today_date()
        }
        
        with open(DAILY_GATE_LOG_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')


class SignalConsumer:
    """Read-only signal consumer from Anchor backend"""
    
    @staticmethod
    def fetch_latest_signal() -> Optional[Dict[str, Any]]:
        """Fetch latest signal from backend (read-only)"""
        try:
            response = requests.get(f"{API_BASE}/signal/latest", timeout=10)
            
            if response.status_code == 404:
                print("ℹ️ No signal available (AWAITING_EXECUTION)")
                return None
            
            if response.status_code == 403:
                print("⚠️ Market closed")
                return None
            
            if response.ok:
                signal = response.json()
                print(f"✅ Fetched signal: {signal.get('signal_id')}")
                return signal
            
            print(f"❌ API error: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"❌ Failed to fetch signal: {e}")
            return None
    
    @staticmethod
    def is_signal_valid(signal: Dict[str, Any]) -> bool:
        """Check if signal is still valid (within TTL)"""
        if not signal:
            return False
        
        # Check if signal has validity field
        validity = signal.get('validity')
        if validity != 'ACTIVE':
            print(f"⚠️ Signal validity: {validity}")
            return False
        
        # Check timestamp (signals should be fresh)
        signal_time = signal.get('executed_at') or signal.get('timestamp')
        if not signal_time:
            print("⚠️ Signal missing timestamp")
            return False
        
        try:
            sig_dt = datetime.fromisoformat(signal_time.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age_minutes = (now - sig_dt).total_seconds() / 60
            
            # Signal should be executed within reasonable time (e.g., 90 min TTL)
            if age_minutes > 90:
                print(f"⚠️ Signal expired (age: {age_minutes:.1f} min)")
                return False
            
            print(f"✅ Signal valid (age: {age_minutes:.1f} min)")
            return True
            
        except Exception as e:
            print(f"⚠️ Error validating signal timestamp: {e}")
            return False


class ExecutionAdapter:
    """Stateless execution adapter - no decision making"""
    
    @staticmethod
    def execute_to_mt4_demo(signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute signal to MT4 Demo
        
        NOTE: This is a PLACEHOLDER for actual MT4 integration.
        In production, this would use MT4 API or bridge.
        
        For AUTO v0 proof, we simulate execution and log it.
        """
        start_time = datetime.now(timezone.utc)
        
        # Simulate MT4 execution (replace with actual MT4 API call)
        execution_result = {
            "signal_id": signal['signal_id'],
            "signal_time": signal.get('executed_at') or signal.get('timestamp'),
            "auto_order_time": start_time.isoformat(),
            "signal_price": signal['entry'],
            "execution_price": signal['entry'],  # In real MT4, this would be actual fill price
            "direction": signal['direction'],
            "tp": signal['tp'],
            "sl": signal['sl'],
            "confidence": signal['confidence'],
            "status": "EXECUTED",
            "latency_ms": 0,  # Will be calculated
            "mt4_order_id": None,  # Placeholder for actual MT4 order ID
            "execution_mode": "DEMO_SIMULATION"  # Mark as simulation for AUTO v0
        }
        
        end_time = datetime.now(timezone.utc)
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        execution_result['latency_ms'] = latency_ms
        
        # Validate latency
        if latency_ms > MAX_LATENCY_MS:
            print(f"⚠️ High latency: {latency_ms}ms (max: {MAX_LATENCY_MS}ms)")
            execution_result['status'] = 'EXECUTED_HIGH_LATENCY'
        
        return execution_result
    
    @staticmethod
    def log_execution(execution_result: Dict[str, Any]):
        """Append execution log (immutable)"""
        with open(EXECUTION_LOG_FILE, 'a') as f:
            f.write(json.dumps(execution_result) + '\n')
        
        print(f"📝 Logged execution: {execution_result['signal_id']}")


def run_auto_v0():
    """
    Main AUTO v0 execution loop
    
    This function:
    1. Checks daily execution gate
    2. Fetches signal (read-only)
    3. Validates signal
    4. Executes if all constraints pass
    5. Logs everything (append-only)
    """
    print("=" * 60)
    print("AUTO v0 - Execution Cycle")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # Step 1: Check daily gate
    if DailyExecutionGate.has_executed_today():
        print("🚫 Daily execution cap reached (1/day)")
        return
    
    # Step 2: Fetch signal (read-only)
    signal = SignalConsumer.fetch_latest_signal()
    if not signal:
        DailyExecutionGate.log_gate_decision(
            "N/A", 
            "SKIP", 
            "No signal available"
        )
        return
    
    signal_id = signal.get('signal_id', 'UNKNOWN')
    
    # Step 3: Validate signal
    if not SignalConsumer.is_signal_valid(signal):
        DailyExecutionGate.log_gate_decision(
            signal_id,
            "SKIP",
            "Signal invalid or expired"
        )
        return
    
    # Step 4: Log gate decision (EXECUTE)
    DailyExecutionGate.log_gate_decision(
        signal_id,
        "EXECUTE",
        "Signal valid, gate open, executing"
    )
    
    # Step 5: Execute (stateless)
    print(f"🚀 Executing signal: {signal_id}")
    execution_result = ExecutionAdapter.execute_to_mt4_demo(signal)
    
    # Step 6: Log execution (append-only)
    ExecutionAdapter.log_execution(execution_result)
    
    print("=" * 60)
    print(f"✅ AUTO v0 execution complete: {signal_id}")
    print(f"Latency: {execution_result['latency_ms']}ms")
    print("=" * 60)


if __name__ == "__main__":
    run_auto_v0()
