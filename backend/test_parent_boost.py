import httpx
import asyncio

PARENT_URL = "http://ai-garbage-parent:8004/predict"

async def test_parent_logic():
    print(f"Testing Parent Logic at {PARENT_URL}...")
    
    # Payload simulating a "Huge Garbage Pile"
    # Coverage 0.6 (60%), Dirtiness 0.8 (Very Dirty), No specific risk keywords
    payload = {
        "object_count": 10.0,
        "coverage_area": 0.6,
        "dirtiness_score": 0.8,
        "location_multiplier": 0.5,
        "text_severity": 0.5,
        "social_score": 0.2,
        "risk_factor": 0.0 # No toxic risk, just visual mess
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(PARENT_URL, json=payload, timeout=5.0)
            data = resp.json()
            print(f"Input Coverage: {payload['coverage_area']}")
            print(f"Input Dirtiness: {payload['dirtiness_score']}")
            print(f"Output Score: {data['severity_score']}")
            print(f"Output Level: {data['severity_level']}")
            
            # Logic Check: 
            # Base approx: (60*0.45 = 27) + (80*0.35 = 28) + (50*0.1=5) + (50*0.2=10) + (20*0.1=2) = ~72
            # Boost (Cov > 0.4): 72 * 1.25 = 90
            # Should be CRITICAL (>=80)
            
            if data['severity_score'] > 80:
                print("✅ BOOST LOGIC VERIFIED: Score is Critical (>80) for visual mess.")
            else:
                print("❌ LOGIC FAILURE: Score too low.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_parent_logic())
