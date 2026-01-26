"""
Proof Packet Generator
Creates evidence package for investor review
"""
import os
import json
import requests
from datetime import datetime

def generate_proof_packet():
    """Generate proof packet with all evidence"""
    
    print("=" * 60)
    print("QUANTIX SYSTEM PROOF PACKET")
    print(f"Generated: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 1. Health Check
    print("\n1. SYSTEM HEALTH")
    try:
        r = requests.get("http://localhost:8080/health", timeout=5)
        health = r.json()
        print(f"   Status: {health.get('status')}")
        print(f"   Market Open: {health.get('market_open')}")
        print(f"   Telegram: {health.get('telegram_token_set')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Data Feed Health
    print("\n2. DATA FEED STATUS")
    try:
        r = requests.get("http://localhost:8080/data-feed/health", timeout=5)
        feed = r.json()
        print(f"   Provider: {feed.get('provider')}")
        print(f"   Status: {feed.get('status')}")
        print(f"   Last Price: {feed.get('last_price')}")
        print(f"   Timestamp: {feed.get('timestamp')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Latest Logs
    print("\n3. LATEST ACTIVITY")
    try:
        if os.path.exists("daily_gate_log.jsonl"):
            with open("daily_gate_log.jsonl", 'r') as f:
                lines = f.readlines()
                if lines:
                    last_log = json.loads(lines[-1])
                    print(f"   Last Decision: {last_log.get('decision')}")
                    print(f"   Reason: {last_log.get('reason')}")
                    print(f"   Date: {last_log.get('date')}")
                    print(f"   Timestamp: {last_log.get('timestamp')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Daily Summary
    print("\n4. DAILY SUMMARY")
    try:
        if os.path.exists("daily_summary_log.jsonl"):
            with open("daily_summary_log.jsonl", 'r') as f:
                lines = f.readlines()
                if lines:
                    summary = json.loads(lines[-1])
                    print(f"   Date: {summary.get('date')}")
                    print(f"   Signals Seen: {summary.get('signals_seen')}")
                    print(f"   Executions: {summary.get('executions')}")
                    print(f"   Skipped: {summary.get('skipped')}")
                    print(f"   Violations: {summary.get('violations')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Environment Check
    print("\n5. CONFIGURATION")
    print(f"   API Key Set: {bool(os.getenv('TWELVE_DATA_API_KEY'))}")
    print(f"   AUTO v0 Enabled: {os.getenv('AUTO_V0_ENABLED', 'Not Set')}")
    
    print("\n" + "=" * 60)
    print("✅ PROOF PACKET COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    generate_proof_packet()
