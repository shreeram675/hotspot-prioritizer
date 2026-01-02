import httpx
import time

BASE_URL = "http://localhost:8000"

# Register and login
unique_id = int(time.time())
email = f"test_{unique_id}@example.com"
password = "password123"

print("Registering user...")
httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "name": "Test User", "role": "citizen"})

print("Logging in...")
login_resp = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create sample reports at the location shown in screenshot
lat = "12.9466368"
lon = "77.6175616"

sample_reports = [
    {
        "title": "Garbage pile on street",
        "category": "Sanitation",
        "description": "Large pile of garbage accumulating on the roadside. Needs immediate attention.",
        "lat": lat,
        "lon": lon
    },
    {
        "title": "Waste management issue",
        "category": "Sanitation", 
        "description": "Garbage not being collected regularly in this area. Bad smell.",
        "lat": "12.9466500",  # Very close
        "lon": "77.6175700"
    },
    {
        "title": "Pothole on main road",
        "category": "Infrastructure",
        "description": "Deep pothole causing traffic issues.",
        "lat": "12.9466200",  # Nearby but different issue
        "lon": "77.6175500"
    }
]

print("\nCreating sample reports...")
for i, report_data in enumerate(sample_reports, 1):
    files = {'image': ('test.jpg', b'fake_image_data', 'image/jpeg')}
    resp = httpx.post(f"{BASE_URL}/reports/", data=report_data, files=files, headers=headers)
    if resp.status_code == 200:
        print(f"✅ Created report {i}: {report_data['title']}")
    else:
        print(f"❌ Failed to create report {i}: {resp.text}")

print("\n✅ Sample data created! Now try submitting a report about 'garbage' at that location.")
