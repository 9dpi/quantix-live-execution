from supabase import create_client, Client
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

supabase: Client | None = None

def init_supabase():
    """
    Standardize Supabase initialization.
    No proxy, no headers, no options.
    """
    global supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        logger.warning("Supabase credentials missing. DB features disabled.")
        return None

    try:
        supabase = create_client(url, key)
        logger.info("Supabase initialized successfully")
    except Exception as e:
        logger.error(f"Supabase init failed: {e}")
        supabase = None

    return supabase

def get_supabase() -> Optional[Client]:
    """Get the initialized supabase client"""
    return supabase

def is_db_connected() -> bool:
    """Check if database is connected and responsive"""
    return supabase is not None

# --- Database Operations ---

def save_signal_to_db(signal: Dict) -> Optional[str]:
    """Save signal to Supabase database"""
    client = get_supabase()
    if not client:
        return None
    
    try:
        price_levels = signal.get("price_levels", {})
        entry_zone = price_levels.get("entry_zone", ["0", "0"])
        trade_details = signal.get("trade_details", {})
        
        data = {
            "asset": signal.get("asset", "EUR/USD"),
            "market": "forex",
            "timeframe": signal.get("timeframe", "M15"),
            "session": signal.get("session", "Intraday"),
            "trade_direction": signal.get("direction", "BUY"),
            "entry_min": float(entry_zone[0]),
            "entry_max": float(entry_zone[1]),
            "take_profit": float(price_levels.get("take_profit", 0)),
            "stop_loss": float(price_levels.get("stop_loss", 0)),
            "target_pips": int(trade_details.get("target_pips", 0)),
            "risk_reward": trade_details.get("risk_reward", "1:1"),
            "confidence": float(signal.get("confidence", 0)),
            "confidence_tier": signal.get("confidence_tier", "LOW"),
            "trade_type": signal.get("trade_type", "Intraday"),
            "engine_version": "quantix-core-3.1",
            "source": signal.get("source", "AI"),
            "is_active": True
        }
        
        response = client.table("signals").insert(data).execute()
        
        if response.data:
            signal_id = response.data[0]["id"]
            save_signal_snapshot(signal_id, signal)
            return signal_id
            
    except Exception as e:
        logger.error(f"Failed to save signal: {e}")
    return None

def save_signal_snapshot(signal_id: str, signal: Dict) -> bool:
    client = get_supabase()
    if not client: return False
    try:
        data = {"signal_id": signal_id, "snapshot": signal}
        client.table("signal_snapshots").insert(data).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")
        return False

def get_active_signals(limit: int = 10) -> List[Dict]:
    client = get_supabase()
    if not client: return []
    try:
        response = client.table("signals")\
            .select("*")\
            .eq("is_active", True)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Failed to fetch active signals: {e}")
        return []
