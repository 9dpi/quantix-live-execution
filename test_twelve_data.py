"""
Test Twelve Data API connection
Verifies that the API key is valid and data can be fetched
"""
import os
import requests
from datetime import datetime

# Set API key for this session (since setx requires new terminal)
os.environ["TWELVE_DATA_API_KEY"] = "4a64fb7beafc42e6a9d6b0576ce5cf9f"

def test_twelve_data():
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    
    if not api_key:
        print("❌ TWELVE_DATA_API_KEY not set!")
        return False
    
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        response = requests.get(
            "https://api.twelvedata.com/price",
            params={
                "symbol": "EUR/USD",
                "apikey": api_key
            },
            timeout=10
        )
        
        print(f"📡 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data}")
            
            if "price" in data:
                price = float(data["price"])
                print(f"💰 EUR/USD Price: {price}")
                print(f"⏰ Timestamp: {datetime.now().isoformat()}")
                print("\n✅ DATA FEED VERIFIED – Ready to proceed!")
                return True
            else:
                print(f"⚠️ No price in response: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_twelve_data()
    exit(0 if success else 1)
