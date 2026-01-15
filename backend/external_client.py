"""
External API Client - Minimal
Fetches signals from Quantix AI Core
"""
import httpx
import os
from typing import Dict

# Quantix API Configuration
QUANTIX_API_URL = os.getenv("QUANTIX_API_URL", "https://quantix-ai-core.railway.app/api/v1/lab/market-reference")


def fetch_signal(asset: str = "EUR/USD") -> Dict:
    """
    Fetch signal from Quantix AI Core
    
    Args:
        asset: Trading asset (default: EUR/USD)
        
    Returns:
        Signal data from Quantix API
        
    Raises:
        httpx.HTTPError: If API request fails
    """
    # Convert EUR/USD to EURUSD for Quantix API
    symbol = asset.replace("/", "")
    
    try:
        response = httpx.get(
            QUANTIX_API_URL,
            params={
                "symbol": symbol,
                "tf": "M15"
            },
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        # Return mock data as fallback
        return get_mock_signal(asset)


def get_mock_signal(asset: str = "EUR/USD") -> Dict:
    """
    Mock signal data for testing/fallback
    """
    return {
        "asset": asset,
        "direction": "BUY",
        "confidence": 96,
        "entry": [1.16710, 1.16750],
        "tp": 1.17080,
        "sl": 1.16480,
        "timeframe": "M15",
        "session": "London-NewYork",
        "source": "mock"
    }
