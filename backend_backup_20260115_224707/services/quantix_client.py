"""
Quantix AI Core Client
Handles communication with Quantix AI Core API
"""

import os
import requests
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Configuration
QUANTIX_BASE_URL = os.getenv("QUANTIX_CORE_BASE_URL", "https://quantix-ai-core.yourdomain.com")
API_KEY = os.getenv("QUANTIX_API_KEY", "")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def fetch_quantix_signal(payload: Dict) -> Dict:
    """
    Call Quantix AI Core and return raw signal
    
    Args:
        payload: Request payload with asset, timeframe, session, mode
        
    Returns:
        Dict: Signal data from Quantix AI Core
        
    Raises:
        requests.RequestException: If API call fails
    """
    try:
        logger.info(f"Calling Quantix AI Core for {payload.get('asset')}")
        
        resp = requests.post(
            f"{QUANTIX_BASE_URL}/v1/signal/generate",
            json=payload,
            headers=HEADERS,
            timeout=3
        )
        
        resp.raise_for_status()
        data = resp.json()
        
        logger.info(f"Received signal with confidence: {data.get('confidence')}")
        return data
        
    except requests.Timeout:
        logger.error("Quantix API timeout")
        raise
    except requests.RequestException as e:
        logger.error(f"Quantix API error: {e}")
        raise
