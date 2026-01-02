import httpx
import time

BASE_URL = "http://localhost:8000"

def verify_duplicates():
    print("=== Duplicate Detection Verification ===")
    
    # 1. Login
    # 1. Login / Register
    import time
    unique_id = int(time.time())
    email = f"admin_{unique_id}@example.com"
    password = "password123"
    
    try:
        # Register first
        print(f"Registering {email}...")
        reg_resp = httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "name": "Admin", "role": "admin"})
        
        login_resp = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
            
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in.")
    except Exception as e:
        print(f"❌ Connection Error (App might not be up yet): {e}")
        return

    # 2. Create Base Report
    print("\n[Setup] Creating Base Report at Lat=12.97, Lon=77.59...")
    files = {'image': ('test.jpg', b'fake_image_bytes', 'image/jpeg')}
    data = {
        "title": "Broken Streetlight",
        "category": "Infrastructure",
        "description": "The streetlight on the corner is flickering and dark.",
        "lat": "12.97000",
        "lon": "77.59000"
    }
    resp = httpx.post(f"{BASE_URL}/reports/", data=data, files=files, headers=headers)
    if resp.status_code == 200:
        print(f"✅ Report Created: ID {resp.json()['report_id']}")
    else:
        print(f"❌ Failed to create report: {resp.text}")
        return

    # 3. Test Cases
    
    # Case A: Nearby (Same Location), Similar Text
    print("\n[Test A] Check Duplicate: Nearby + Similar Text")
    check_data = {
        "description": "Streetlight is broken and dark.", # Similar text
        "lat": "12.97001", # Very close (~1.1m away)
        "lon": "77.59000"
    }
    dupes = httpx.post(f"{BASE_URL}/reports/check-duplicates", data=check_data, headers=headers).json()
    if len(dupes) > 0:
        print(f"✅ SUCCESS: Found {len(dupes)} duplicates. Top match: {dupes[0]['title']} ({dupes[0]['similarity']})")
        print(f"   Distance: {dupes[0].get('distance_m')}m")
    else:
        print("❌ FAILURE: Expected duplicate, found none.")

    # Case B: Far Away, Same Text
    print("\n[Test B] Check Duplicate: Far Away (>50m) + Same Text")
    check_data_far = {
        "description": "The streetlight on the corner is flickering and dark.", # Exact text
        "lat": "12.98000", # ~1.1km away
        "lon": "77.59000"
    }
    dupes_far = httpx.post(f"{BASE_URL}/reports/check-duplicates", data=check_data_far, headers=headers).json()
    if len(dupes_far) == 0:
        print("✅ SUCCESS: Found 0 duplicates (as expected, too far).")
    else:
        print(f"❌ FAILURE: Expected 0 duplicates, found {len(dupes_far)}.")
        print(dupes_far)

    # Case C: Nearby, Different Text
    print("\n[Test C] Check Duplicate: Nearby + Different Text")
    check_data_diff = {
        "description": "I lost my dog here. He is brown and cute.", # Completely different topic
        "lat": "12.97000",
        "lon": "77.59000"
    }
    dupes_diff = httpx.post(f"{BASE_URL}/reports/check-duplicates", data=check_data_diff, headers=headers).json()
    # Should probably be 0, or very low score. Threshold is 0.5 in backend.
    if len(dupes_diff) == 0:
        print("✅ SUCCESS: Found 0 duplicates (as expected, text differs).")
    else:
        print(f"⚠️ Warning: Found {len(dupes_diff)} duplicates. Score might be too lenient?")
        print(dupes_diff)

if __name__ == "__main__":
    verify_duplicates()
