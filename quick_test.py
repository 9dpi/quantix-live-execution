import requests
import json

BASE_URL = "https://signalgeniusai-production.up.railway.app"

print("="*60)
print("  SIGNAL GENIUS AI - API TEST")
print("="*60)

# Test 1: Latest Signal
print("\n1. Testing /api/v1/signal/latest")
print("-"*60)
response = requests.get(f"{BASE_URL}/api/v1/signal/latest")
data = response.json()
print(json.dumps(data, indent=2))

# Test 2: Legacy Endpoint
print("\n2. Testing /api/v1/lab/market-reference")
print("-"*60)
response = requests.get(f"{BASE_URL}/api/v1/lab/market-reference?symbol=EURUSD&tf=M15")
data = response.json()
print(json.dumps(data, indent=2))

print("\n" + "="*60)
print("  ✅ ALL TESTS COMPLETED")
print("="*60)
