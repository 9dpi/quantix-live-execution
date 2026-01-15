"""
Signal Genius AI - API Test Script
Tests all endpoints on Railway deployment
"""

import requests
import json
from datetime import datetime

# Railway URL - Update this with your actual URL
RAILWAY_URL = "https://signal-genius-ai-production.up.railway.app"

# Alternative URLs to try
POSSIBLE_URLS = [
    "https://signal-genius-ai-production.up.railway.app",
    "https://signal-genius-ai.up.railway.app",
    "https://signalgeniusai-production.up.railway.app"
]

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_result(success, message):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_health(base_url):
    """Test health check endpoint"""
    print_header("Test 1: Health Check")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_result(False, f"Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Health check failed: {e}")
        return False

def test_root(base_url):
    """Test root endpoint"""
    print_header("Test 2: Root Endpoint")
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Root endpoint accessible")
            print(f"   Name: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print_result(False, f"Root endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Root endpoint failed: {e}")
        return False

def test_latest_signal(base_url):
    """Test latest signal endpoint"""
    print_header("Test 3: Latest Signal")
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/signal/latest",
            params={"asset": "EUR/USD"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "no_signal":
                print_result(True, "API working - No high-confidence signal available")
                print(f"   Confidence: {data.get('confidence')}%")
                print(f"   Threshold: {data.get('threshold')}%")
            else:
                print_result(True, "Signal received successfully")
                print(f"   Asset: {data.get('asset')}")
                print(f"   Direction: {data.get('trade')}")
                print(f"   Confidence: {data.get('confidence')}%")
                print(f"   Entry: {data.get('entry')}")
                print(f"   TP: {data.get('tp')}")
                print(f"   SL: {data.get('sl')}")
                print(f"   Source: {data.get('source')}")
            return True
        else:
            print_result(False, f"Latest signal failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Latest signal failed: {e}")
        return False

def test_active_signals(base_url):
    """Test active signals endpoint"""
    print_header("Test 4: Active Signals from Database")
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/signals/active",
            params={"limit": 5},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_result(True, f"Active signals retrieved: {count} signals")
            
            if count > 0:
                print("\n   Recent signals:")
                for i, signal in enumerate(data.get('signals', [])[:3], 1):
                    print(f"   {i}. {signal.get('asset')} {signal.get('trade_direction')} - {signal.get('confidence')}%")
            return True
        else:
            print_result(False, f"Active signals failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Active signals failed: {e}")
        return False

def test_legacy_endpoint(base_url):
    """Test legacy market-reference endpoint"""
    print_header("Test 5: Legacy Endpoint (Compatibility)")
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/lab/market-reference",
            params={"symbol": "EURUSD", "tf": "M15"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "message" in data:
                print_result(True, "Legacy endpoint working - No signal")
                print(f"   Message: {data.get('message')}")
            else:
                print_result(True, "Legacy endpoint working - Signal received")
                print(f"   Asset: {data.get('asset')}")
                print(f"   Direction: {data.get('direction')}")
                print(f"   Confidence: {data.get('confidence')}%")
            return True
        else:
            print_result(False, f"Legacy endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Legacy endpoint failed: {e}")
        return False

def find_working_url():
    """Try to find the working Railway URL"""
    print_header("Finding Railway URL")
    
    for url in POSSIBLE_URLS:
        print(f"\nTrying: {url}")
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print_result(True, f"Found working URL: {url}")
                return url
        except:
            print_result(False, f"Not accessible: {url}")
    
    return None

def run_all_tests(base_url):
    """Run all API tests"""
    print("\n" + "🚀 " + "="*58)
    print("   SIGNAL GENIUS AI - API TEST SUITE")
    print("="*60)
    print(f"\nTesting API at: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health(base_url)))
    results.append(("Root Endpoint", test_root(base_url)))
    results.append(("Latest Signal", test_latest_signal(base_url)))
    results.append(("Active Signals", test_active_signals(base_url)))
    results.append(("Legacy Endpoint", test_legacy_endpoint(base_url)))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\n{'='*60}")
    print(f"   Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("   🎉 All tests passed! API is working correctly.")
    elif passed > 0:
        print("   ⚠️  Some tests failed. Check configuration.")
    else:
        print("   ❌ All tests failed. API might not be deployed.")
    
    print("="*60)

if __name__ == "__main__":
    # Try to find working URL
    working_url = find_working_url()
    
    if working_url:
        run_all_tests(working_url)
    else:
        print("\n❌ Could not find working Railway URL.")
        print("\nPlease provide the correct URL and update RAILWAY_URL in this script.")
        print("\nYou can find it in Railway dashboard:")
        print("  1. Go to your project")
        print("  2. Click on the service")
        print("  3. Look for 'Domains' section")
        print("  4. Copy the .railway.app URL")
