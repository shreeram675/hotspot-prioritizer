"""
Test script to verify the dual-domain severity analysis system on Docker ports
"""
import requests
import json
import time

BASE_URL = "http://localhost:8005"  # Docker mapped backend port

def wait_for_backend(retries=10, delay=5):
    print(f"Waiting for backend at {BASE_URL}...")
    for i in range(retries):
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("✅ Backend is up!")
                return True
        except:
            pass
        print(f"   Retry {i+1}/{retries}...")
        time.sleep(delay)
    print("❌ Backend failed to start")
    return False

def test_reports_endpoint():
    """Test if reports endpoint works"""
    try:
        response = requests.get(f"{BASE_URL}/reports")
        if response.status_code == 200:
            reports = response.json()
            print(f"✅ Reports endpoint working - Found {len(reports)} reports")
            return True
        else:
            print(f"❌ Reports endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Reports endpoint failed: {e}")
        return False

def test_ai_services():
    """Test if AI services are accessible"""
    services = {
        "Pothole Child": "http://localhost:8001/health",
        "Pothole Parent": "http://localhost:8003/health",
        "Garbage Child": "http://localhost:8002/health",
        "Garbage Parent": "http://localhost:8004/health"
    }
    
    results = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} service is running")
                results[name] = True
            else:
                print(f"⚠️  {name} service returned {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"❌ {name} service error: {e}")
            results[name] = False
    
    return all(results.values())

def main():
    print("=" * 60)
    print("Testing Docker Stack")
    print("=" * 60)
    
    if wait_for_backend():
        test_reports_endpoint()
        test_ai_services()
    else:
        print("Skipping further tests as backend is down")

if __name__ == "__main__":
    main()
