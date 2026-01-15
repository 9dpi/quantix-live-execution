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

if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
else:
    logger.warning("Supabase not configured. Database features disabled.")

def save_signal_to_db(signal: Dict) -> Optional[str]:
    """
    Save signal to Supabase database
    
    Args:
        signal: Normalized signal data
        
    Returns:
        str: Signal ID if successful, None otherwise
    """
    if not supabase:
        logger.warning("Supabase not available. Skipping database save.")
        return None
    
    try:
        # Prepare data for database
        entry = signal.get("entry", [0, 0])
        
        data = {
            "asset": signal.get("asset", "EUR/USD"),
            "market": "forex",
            "timeframe": "M15",
            "session": "London-NewYork",
            "trade_direction": signal.get("trade", "BUY"),
            "entry_min": float(entry[0]) if isinstance(entry, list) else float(entry),
            "entry_max": float(entry[1]) if isinstance(entry, list) and len(entry) > 1 else float(entry),
            "take_profit": float(signal.get("tp", 0)),
            "stop_loss": float(signal.get("sl", 0)),
            "target_pips": signal.get("target_pips", 0),
            "risk_reward": float(signal.get("risk_reward", "1:1").split(":")[-1].strip()) if isinstance(signal.get("risk_reward"), str) else 1.0,
            "confidence": float(signal.get("confidence", 0)),
            "trade_type": "intraday",
            "engine_version": "quantix-core",
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
    """
    Save signal snapshot to database
    
    Args:
        signal_id: Signal UUID
        signal: Full signal data
        
    Returns:
        bool: True if successful
    """
    if not supabase:
        return False
    
    try:
        data = {
            "signal_id": signal_id,
            "snapshot": signal
        }
        
        supabase.table("signal_snapshots").insert(data).execute()
        logger.info(f"Snapshot saved for signal {signal_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")
        return False

def get_active_signals(limit: int = 10) -> List[Dict]:
    """
    Get active signals from database
    
    Args:
        limit: Maximum number of signals to return
        
    Returns:
        List[Dict]: List of active signals
    """
    if not supabase:
        logger.warning("Supabase not available. Returning empty list.")
        return []
    
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

def log_telegram_dispatch(signal_id: str, chat_id: str) -> bool:
    """
    Log Telegram signal dispatch
    
    Args:
        signal_id: Signal UUID
        chat_id: Telegram chat ID
        
    Returns:
        bool: True if successful
    """
    if not supabase:
        return False
    
    try:
        data = {
            "signal_id": signal_id,
            "telegram_chat_id": str(chat_id)
        }
        
        supabase.table("telegram_dispatch_log").insert(data).execute()
        logger.info(f"Telegram dispatch logged for signal {signal_id}")
        return True
        
    except Exception as e:
        # Might fail due to unique constraint if already dispatched
        logger.warning(f"Failed to log dispatch (might be duplicate): {e}")
        return False

def check_signal_dispatched(signal_id: str, chat_id: str) -> bool:
    """
    Check if signal was already dispatched to chat
    
    Args:
        signal_id: Signal UUID
        chat_id: Telegram chat ID
        
    Returns:
        bool: True if already dispatched
    """
    if not supabase:
        return False
    
    try:
        response = supabase.table("telegram_dispatch_log")\
            .select("id")\
            .eq("signal_id", signal_id)\
            .eq("telegram_chat_id", str(chat_id))\
            .execute()
        
        return len(response.data) > 0 if response.data else False
        
    except Exception as e:
        logger.error(f"Failed to check dispatch status: {e}")
        return False
