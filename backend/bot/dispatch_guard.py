"""
Dispatch Guard - Anti-Spam Logic
Prevents duplicate signals and manages sending rules
"""
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional


STATE_FILE = "dispatch_state.json"


def load_state() -> Dict:
    """Load dispatch state from file"""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading state: {e}")
        return {}


def save_state(state: Dict) -> None:
    """Save dispatch state to file"""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving state: {e}")


def should_dispatch(data: dict) -> bool:
    """
    Determine if signal should be sent to Telegram.
    
    Rules (Phase G Sync):
    - R1: Only send if 'meta.status' is 'fresh' (Block replays)
    - R2: Only send if confidence >= 60% (Quality Bar)
    - R3: Don't resend if already sent within current 24h window
    
    Args:
        data: Full API response with payload
        
    Returns:
        bool: True if should send
    """
    if not data or data.get("status") != "ok":
        print("❌ R0: Invalid data")
        return False
    
    p = data.get("payload", {})
    meta = p.get("meta", {})
    confidence = p.get("confidence", 0)
    asset = p.get("symbol") or p.get("asset", "EUR/USD")
    timeframe = p.get("timeframe", "M15")
    
    # R1: Block Replays
    if meta.get("status") == "replay":
        print(f"❌ R1: Blocked Replay signal for {asset}")
        return False
    
    # R2: Confidence Bar (Phase G: >= 60)
    if confidence < 60:
        print(f"❌ R2: Low confidence ({confidence}%). Minimum 60% required for Telegram.")
        return False
    
    # R3: Dispatch History Check
    key = f"{asset}_{timeframe}"
    state = load_state()
    last = state.get(key)
    now = datetime.now(timezone.utc)
    
    if last:
        try:
            last_time = datetime.fromisoformat(last["last_sent"])
            # Already checked R1 (freshness), but R3 adds extra protection
            if now - last_time < timedelta(hours=24):
                print(f"❌ R3: Already sent a signal for {key} in the last 24h")
                return False
        except Exception:
            pass

    # APPROVED
    # Update state
    state[key] = {
        "last_sent": now.isoformat(),
        "direction": p.get("direction"),
        "entry": p.get("entry"),
        "confidence": confidence
    }
    save_state(state)
    
    print(f"✅ DISPATCH APPROVED: {asset} @ {confidence}% (FRESH)")
    return True


def get_dispatch_stats() -> Dict:
    """Get statistics about sent signals"""
    state = load_state()
    return {
        "total_signals": len(state),
        "pairs": list(state.keys()),
        "state": state
    }


def reset_state() -> None:
    """Reset dispatch state (use with caution)"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print("✅ Dispatch state reset")
