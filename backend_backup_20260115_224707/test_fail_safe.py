"""
Test Fail-Safe Mechanisms
Verify API never returns 500 errors even when infrastructure fails
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"  # Change to Railway URL when testing production

def test_health_check():
    """Test 1: /health should always return 200"""
    print("\n🧪 TEST 1: Health Check")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"📊 Response: {json.dumps(data, indent=2)}")
        
        # Verify structure
        assert response.status_code == 200, "Health check should return 200"
        assert "status" in data, "Response should have 'status' field"
        assert "database" in data, "Response should have 'database' field"
        
        db_status = data.get("database")
        if db_status == "disconnected":
            print("⚠️  Database is DISCONNECTED (degraded mode)")
        else:
            print("✅ Database is CONNECTED")
            
        print("✅ TEST 1 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}\n")
        return False


def test_latest_signal():
    """Test 2: /api/v1/signal/latest should never return 500"""
    print("\n🧪 TEST 2: Latest Signal Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/signal/latest", timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        # CRITICAL: Should NEVER be 500
        assert response.status_code != 500, "❌ FAIL: API returned 500 error!"
        assert response.status_code == 200, "Should return 200 even in degraded mode"
        
        data = response.json()
        print(f"📊 Response: {json.dumps(data, indent=2)}")
        
        # Check response type
        if data.get("status") == "degraded":
            print("⚠️  API is in DEGRADED MODE (DB unavailable)")
            print("✅ But API still returned valid JSON (no crash)")
        elif data.get("status") == "no_signal":
            print("ℹ️  No signal available (low confidence)")
        elif data.get("status") == "error":
            print("⚠️  Service error but handled gracefully")
        else:
            print("✅ Signal returned successfully")
            
            # Verify signal structure
            if "asset" in data:
                print(f"   Asset: {data.get('asset')}")
                print(f"   Direction: {data.get('direction')}")
                print(f"   Confidence: {data.get('confidence')}%")
                
                # Check DB status
                if data.get("status_db") == "disconnected":
                    print("   ⚠️  Running in reference-only mode (DB down)")
        
        print("✅ TEST 2 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}\n")
        return False


def test_active_signals():
    """Test 3: /api/v1/signals/active should never crash"""
    print("\n🧪 TEST 3: Active Signals Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/signals/active", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        # Should never be 500
        assert response.status_code != 500, "❌ FAIL: API returned 500 error!"
        assert response.status_code == 200, "Should return 200 even if DB is down"
        
        data = response.json()
        print(f"📊 Response: {json.dumps(data, indent=2)}")
        
        # Check response
        if data.get("status") == "degraded":
            print("⚠️  Database unavailable - returned empty list")
            assert data.get("count") == 0, "Count should be 0 when degraded"
            assert data.get("signals") == [], "Signals should be empty array"
        elif data.get("status") == "error":
            print("⚠️  Error occurred but handled gracefully")
            assert data.get("count") == 0, "Count should be 0 on error"
        else:
            print(f"✅ Found {data.get('count')} active signals")
        
        print("✅ TEST 3 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}\n")
        return False


def run_all_tests():
    """Run all fail-safe tests"""
    print("\n" + "=" * 50)
    print("🚀 FAIL-SAFE TEST SUITE")
    print("=" * 50)
    print(f"Testing: {BASE_URL}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Latest Signal", test_latest_signal()))
    results.append(("Active Signals", test_active_signals()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - API IS FAIL-SAFE!")
    else:
        print("\n⚠️  SOME TESTS FAILED - NEEDS ATTENTION")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
