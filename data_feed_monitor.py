"""
Data Feed Health Monitor
Tracks the health of external data providers (Twelve Data)
"""
import os
import json
import requests
from datetime import datetime, timezone
from typing import Dict, Any

DATA_FEED_HEALTH_FILE = "data_feed_health.json"

class DataFeedMonitor:
    """Monitor external data feed health"""
    
    @staticmethod
    def check_twelve_data() -> Dict[str, Any]:
        """
        Check Twelve Data API health
        Returns health status with timestamp
        """
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        
        if not api_key:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "provider": "twelve_data",
                "status": "error",
                "reason": "API key not configured"
            }
        
        try:
            response = requests.get(
                "https://api.twelvedata.com/price",
                params={
                    "symbol": "EUR/USD",
                    "apikey": api_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "price" in data:
                    return {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "provider": "twelve_data",
                        "status": "ok",
                        "last_price": float(data["price"]),
                        "symbol": "EUR/USD"
                    }
                else:
                    return {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "provider": "twelve_data",
                        "status": "error",
                        "reason": f"No price in response: {data}"
                    }
            else:
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": "twelve_data",
                    "status": "error",
                    "reason": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "provider": "twelve_data",
                "status": "error",
                "reason": str(e)
            }
    
    @staticmethod
    def save_health_status(status: Dict[str, Any]):
        """Save health status to file"""
        with open(DATA_FEED_HEALTH_FILE, 'w') as f:
            json.dump(status, f, indent=2)
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """Get last saved health status"""
        try:
            if os.path.exists(DATA_FEED_HEALTH_FILE):
                with open(DATA_FEED_HEALTH_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "timestamp": None,
            "provider": "twelve_data",
            "status": "unknown",
            "reason": "No health check performed yet"
        }
    
    @staticmethod
    def run_health_check():
        """Run health check and save result"""
        status = DataFeedMonitor.check_twelve_data()
        DataFeedMonitor.save_health_status(status)
        
        # Print status
        if status["status"] == "ok":
            print(f"✅ Data feed: ACTIVE (Price: {status.get('last_price')})")
        else:
            print(f"❌ Data feed: INACTIVE ({status.get('reason')})")
        
        return status

if __name__ == "__main__":
    DataFeedMonitor.run_health_check()
