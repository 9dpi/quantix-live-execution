import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TWELVE_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BASE_URL = "https://api.twelvedata.com"

async def fetch_candles(symbol="EUR/USD", interval="15min", limit=50):
    url = f"{BASE_URL}/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": limit,
        "apikey": TWELVE_API_KEY
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    if "values" not in data:
        # Check for error message from Twelve Data
        error_msg = data.get("message", "Invalid candle data from Twelve Data")
        raise ValueError(error_msg)

    # newest → oldest → reverse to get chronological order (oldest to newest)
    return list(reversed(data["values"]))
