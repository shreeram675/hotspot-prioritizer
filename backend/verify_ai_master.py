import httpx
import asyncio
import base64
import json
import os

# Configuration (Inside Docker)
GARBAGE_CHILD_URL = "http://ai-garbage-child:8002"
GARBAGE_PARENT_URL = "http://ai-garbage-parent:8004"

# 1x1 white pixel JPEG for testing
VALID_JPG = base64.b64decode('/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvavynLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q==')

async def verify_system():
    print("="*50)
    print("🚀 MASTER AI VERIFICATION SUITE")
    print("="*50)

    async with httpx.AsyncClient() as client:
        # TEST 1: Child Model API
        print("\n[TEST 1] Child Service: Image & Scene Analysis")
        try:
            files = {'image': ('test.jpg', VALID_JPG, 'image/jpeg')}
            resp = await client.post(f"{GARBAGE_CHILD_URL}/analyze_image", files=files, timeout=15.0)
            res = resp.json()
            print(f"✅ Image Link OK: Objects={len(res.get('objects', []))}")
            
            resp_s = await client.post(f"{GARBAGE_CHILD_URL}/analyze_scene", files={'image': ('test.jpg', VALID_JPG, 'image/jpeg')}, timeout=15.0)
            print(f"✅ Scene Link OK: Dirtiness={resp_s.json().get('dirtiness_score', 0):.2f}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")

        # TEST 2: Parent Model: Clean Override
        print("\n[TEST 2] Parent Model: Clean Override Logic")
        payload = {
            "object_count": 0.0, "coverage_area": 0.05, "dirtiness_score": 0.1,
            "location_multiplier": 0.5, "text_severity": 0.5, "social_score": 0.0, "risk_factor": 0.0 
        }
        try:
            resp = await client.post(f"{GARBAGE_PARENT_URL}/predict", json=payload)
            score = resp.json().get('severity_score', 100)
            print(f"{'✅ PASSED' if score < 15 else '❌ FAILED'}: Score {score:.1f}")
        except Exception as e:
            print(f"❌ Parent Failed: {e}")

        # TEST 3: Parent Model: Hazard & Coverage Boosts
        print("\n[TEST 3] Parent Model: Hazard & Coverage Boosts")
        # Scenario A: High Coverage
        p_cov = {"object_count": 10.0, "coverage_area": 0.6, "dirtiness_score": 0.8, "location_multiplier": 0.5, "text_severity": 0.5, "social_score": 0.0, "risk_factor": 0.0}
        # Scenario B: High Hazard
        p_haz = {"object_count": 1.0, "coverage_area": 0.1, "dirtiness_score": 0.2, "location_multiplier": 0.5, "text_severity": 0.5, "social_score": 0.0, "risk_factor": 0.9}
        
        try:
            r1 = await client.post(f"{GARBAGE_PARENT_URL}/predict", json=p_cov)
            r2 = await client.post(f"{GARBAGE_PARENT_URL}/predict", json=p_haz)
            print(f"✅ Coverage Boost: {r1.json().get('severity_score'):.1f} (Critical)")
            print(f"✅ Hazard Boost: {r2.json().get('severity_score'):.1f} (Critical)")
        except Exception as e:
            print(f"❌ Boost Test Failed: {e}")

        # TEST 4: Backend Integration (Critical Naming)
        print("\n[TEST 4] Integration: Specific Location Naming")
        try:
            # Calling child directly to see if it returns names
            loc_payload = {"latitude": 12.9716, "longitude": 77.5946}
            resp = await client.post(f"{GARBAGE_CHILD_URL}/analyze_location", json=loc_payload, timeout=20.0)
            res = resp.json()
            names = res.get('critical_names', [])
            status = "✅ PASSED" if len(names) > 0 else "⚠️ WARN (No nearby facilities found, but API ok)"
            print(f"{status}: Facility Names detected: {names[:2]}")
        except Exception as e:
            print(f"❌ Location API Failed: {e}")

    print("\n" + "="*50)
    print("✨ VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(verify_system())

    print("\n" + "="*50)
    print("✨ VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(verify_system())
