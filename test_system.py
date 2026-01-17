"""
Test script to verify the dual-domain severity analysis system
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print("✅ Backend is running on port 8000")
        return True
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_reports_endpoint():
    """Test if reports endpoint works"""
    try:
        response = requests.get(f"{BASE_URL}/reports")
        if response.status_code == 200:
            reports = response.json()
            print(f"✅ Reports endpoint working - Found {len(reports)} reports")
            
            # Check if any reports have AI scores
            ai_reports = [r for r in reports if r.get('ai_severity_score')]
            if ai_reports:
                print(f"✅ Found {len(ai_reports)} reports with AI analysis")
                sample = ai_reports[0]
                print(f"   Sample AI scores:")
                print(f"   - Severity: {sample.get('ai_severity_score')}/100")
                print(f"   - Level: {sample.get('ai_severity_level')}")
                if sample.get('category') == 'pothole':
                    print(f"   - Depth: {sample.get('pothole_depth_score')}")
                    print(f"   - Spread: {sample.get('pothole_spread_score')}")
                elif sample.get('category') == 'garbage':
                    print(f"   - Volume: {sample.get('garbage_volume_score')}")
                    print(f"   - Hazard: {sample.get('garbage_waste_type_score')}")
            else:
                print("⚠️  No reports with AI analysis yet")
            return True
        else:
            print(f"❌ Reports endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Reports endpoint failed: {e}")
        return False

def test_sorting():
    """Test severity-based sorting"""
    try:
        response = requests.get(f"{BASE_URL}/reports?sort_by=ai_severity_score&sort_order=desc")
        if response.status_code == 200:
            reports = response.json()
            print(f"✅ Severity sorting works - {len(reports)} reports sorted")
            return True
        else:
            print(f"❌ Sorting failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sorting test failed: {e}")
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
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ {name} service is running")
                results[name] = True
            else:
                print(f"⚠️  {name} service returned {response.status_code}")
                results[name] = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} service not running (expected if not started)")
            results[name] = False
        except Exception as e:
            print(f"❌ {name} service error: {e}")
            results[name] = False
    
    return all(results.values())

def main():
    print("=" * 60)
    print("Testing Dual-Domain Severity Analysis System")
    print("=" * 60)
    print()
    
    print("1. Testing Backend...")
    backend_ok = test_backend_health()
    print()
    
    if backend_ok:
        print("2. Testing Reports Endpoint...")
        test_reports_endpoint()
        print()
        
        print("3. Testing Severity Sorting...")
        test_sorting()
        print()
    
    print("4. Testing AI Services...")
    ai_ok = test_ai_services()
    print()
    
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    if backend_ok:
        print("✅ Backend: Running")
    else:
        print("❌ Backend: Not accessible")
    
    if ai_ok:
        print("✅ AI Services: All running")
    else:
        print("⚠️  AI Services: Not all running (start them manually)")
    
    print()
    print("Next Steps:")
    print("1. Start AI services if not running:")
    print("   cd ai-pothole-child && python main.py")
    print("   cd ai-pothole-parent && python main.py")
    print("   cd ai-garbage-child && python main.py")
    print("   cd ai-garbage-parent && python main.py")
    print()
    print("2. Or use Docker:")
    print("   docker-compose up --build")
    print()
    print("3. Test frontend:")
    print("   Navigate to http://localhost:3000/admin/reports")

if __name__ == "__main__":
    main()
