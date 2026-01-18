import os
import requests

def get_price():
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    # Fail fast if no API key in prod, or use requests to fetch if key exists
    # Assuming environment has key. If not, this might crash or return None depending on impl.
    # User requested explicit crash if down: "Nếu TwelveData down → app crash"
    
    # Simple implementation as requested
    r = requests.get(
        "https://api.twelvedata.com/price",
        params={
            "symbol": "EUR/USD",
            "apikey": api_key
        },
        timeout=5
    )
    r.raise_for_status() # Ensure we crash on 4xx/5xx
    data = r.json()
    if "price" not in data:
         raise ValueError(f"Invalid API response: {data}")
    return float(data["price"])
