import os
import requests
import time

# Alert tracking
_consecutive_failures = 0
_alert_threshold = 2

def get_price():
    global _consecutive_failures
    
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    
    # Fail fast if no API key
    if not api_key:
        raise ValueError("TWELVE_DATA_API_KEY not configured")
    
    # Simple implementation with retry
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.get(
                "https://api.twelvedata.com/price",
                params={
                    "symbol": "EUR/USD",
                    "apikey": api_key
                },
                timeout=5
            )
            r.raise_for_status()  # Ensure we crash on 4xx/5xx
            data = r.json()
            
            if "price" not in data:
                raise ValueError(f"Invalid API response: {data}")
            
            # Reset failure counter on success
            _consecutive_failures = 0
            return float(data["price"])
            
        except Exception as e:
            _consecutive_failures += 1
            
            # Alert if threshold exceeded
            if _consecutive_failures >= _alert_threshold:
                print(f"[ALERT] Market data unavailable – no signals will be generated")
                print(f"[ALERT] Consecutive failures: {_consecutive_failures}")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                print(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Final failure
                raise

