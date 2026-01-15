"""
Supabase Client
Handles database operations for Signal Genius AI
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging

try:
    from supabase import create_client, Client
except ImportError:
    logging.warning("Supabase client not installed. Database features disabled.")
    create_client = None
    Client = None

logger = logging.getLogger(__name__)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Initialize Supabase client
supabase: Optional[Client] = None

# CLEAN INITIALIZATION (Supabase 2.x compatible)
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        # User fix: Do NOT pass proxy or options that might conflict
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase initialized successfully")
    except Exception as e:
        logger.error(f"Supabase init failed: {e}")
        supabase = None
else:
    logger.warning("Supabase not configured. Database features disabled.")

def save_signal_to_db(signal: Dict) -> Optional[str]:
    """
    Save signal to Supabase database (updated for rich format)
    """
    if not supabase:
        logger.warning("Supabase not available. Skipping database save.")
        return None
    
    try:
        # Extract from rich format
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
        
        response = supabase.table("signals").insert(data).execute()
        
        if response.data:
            signal_id = response.data[0]["id"]
            logger.info(f"Signal saved to database: {signal_id}")
            
            # Save snapshot
            save_signal_snapshot(signal_id, signal)
            
            return signal_id
        
    except Exception as e:
        logger.error(f"Failed to save signal to database: {e}")
    
    return None

def save_signal_snapshot(signal_id: str, signal: Dict) -> bool:
    """Save signal snapshot for audit/rendering"""
    if not supabase: return False
    try:
        data = {"signal_id": signal_id, "snapshot": signal}
        supabase.table("signal_snapshots").insert(data).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")
        return False

def get_active_signals(limit: int = 10) -> List[Dict]:
    """Fetch active signals for the UI"""
    if not supabase: return []
    try:
        response = supabase.table("signals")\
            .select("*")\
            .eq("is_active", True)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Failed to fetch active signals: {e}")
        return []

def is_db_connected() -> bool:
    """Check if database is connected and responsive"""
    return supabase is not None
