import httpx
import asyncio

PARENT_URL = "http://ai-garbage-parent:8004/predict"

async def test_clean_logic():
    print(f"Testing Clean Image Logic at {PARENT_URL}...")
    
    # Payload simulating a "Clean Image"
    # Coverage 0.05, Dirtiness 0.1 (Very Clean), but Location/Text adding noise
    payload = {
        "object_count": 0.0,
        "coverage_area": 0.05,
        "dirtiness_score": 0.1,
        "location_multiplier": 0.5, # Mid noise
        "text_severity": 0.5, # Neutral noise
        "social_score": 0.0,
        "risk_factor": 0.0 
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
            # Base calc without override: (5*0.45) + (10*0.35) + (50*0.1) + (50*0.2) = 2.25 + 3.5 + 5 + 10 = 20.75
            # With Override (score * 0.1) -> 2.075
            
            if data['severity_score'] < 15.0:
                print("✅ CLEAN OVERRIDE VERIFIED: Score is Low (<15) for clean image.")
            else:
                print(f"❌ LOGIC FAILURE: Score is {data['severity_score']} (Expected < 15)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_clean_logic())
