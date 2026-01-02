"""
Bangalore Location-Based Model Testing
Creates dummy reports with real Bangalore locations and tests model accuracy
"""
import requests
import json
import time
from typing import List, Dict
import os

# AI Service Configuration
AI_SERVICE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8000"

# Real Bangalore Locations with Expected Outcomes
BANGALORE_TEST_SCENARIOS = [
    # Educational Zones - Should get HIGH priority (1.5x multiplier)
    {
        "name": "Garbage near National Public School, Koramangala",
        "lat": 12.9352,
        "lon": 77.6245,
        "description": "Plastic bottles and food waste scattered near school gate",
        "expected_severity": "High",
        "expected_zone": "educational",
        "expected_multiplier": 1.5,
        "expected_waste": "recyclable",
        "notes": "Should be high priority due to school proximity"
    },
    {
        "name": "Urgent garbage at Bishop Cotton Boys School",
        "lat": 12.9716,
        "lon": 77.5946,
        "description": "URGENT! Overflowing bins, health hazard near children's play area",
        "expected_severity": "Extreme",
        "expected_zone": "educational",
        "expected_multiplier": 1.5,
        "expected_waste": "dry",
        "notes": "School + urgent keywords should elevate to Extreme"
    },
    {
        "name": "Light litter at Christ University",
        "lat": 12.9342,
        "lon": 77.6067,
        "description": "Few wrappers and bottles on campus",
        "expected_severity": "Medium",
        "expected_zone": "educational",
        "expected_multiplier": 1.4,
        "expected_waste": "recyclable",
        "notes": "Light litter but university location should elevate from Low to Medium"
    },
    
    # Healthcare Zones - Should get HIGH priority (1.4x multiplier)
    {
        "name": "Medical waste near Manipal Hospital",
        "lat": 12.9698,
        "lon": 77.7500,
        "description": "Medical waste and syringes found near hospital entrance",
        "expected_severity": "Extreme",
        "expected_zone": "healthcare",
        "expected_multiplier": 1.4,
        "expected_waste": "hazardous",
        "notes": "Hazardous + hospital = Extreme priority"
    },
    {
        "name": "Garbage at Victoria Hospital",
        "lat": 12.9698,
        "lon": 77.5986,
        "description": "Food waste and packaging materials",
        "expected_severity": "High",
        "expected_zone": "healthcare",
        "expected_multiplier": 1.4,
        "expected_waste": "wet",
        "notes": "Hospital proximity should elevate severity"
    },
    
    # Eco-zones / Parks - Should get MEDIUM-HIGH priority (1.3x multiplier)
    {
        "name": "Litter in Cubbon Park",
        "lat": 12.9762,
        "lon": 77.5929,
        "description": "Plastic bottles and food wrappers scattered in park",
        "expected_severity": "Medium",
        "expected_zone": "eco",
        "expected_multiplier": 1.3,
        "expected_waste": "recyclable",
        "notes": "Park location should elevate from Low to Medium"
    },
    {
        "name": "Garbage dump in Lalbagh Botanical Garden",
        "lat": 12.9507,
        "lon": 77.5848,
        "description": "Large pile of mixed waste near garden entrance",
        "expected_severity": "High",
        "expected_zone": "eco",
        "expected_multiplier": 1.3,
        "expected_waste": "dry",
        "notes": "Protected eco-zone with significant waste"
    },
    
    # Residential Areas - Should get SLIGHT priority (1.1x multiplier)
    {
        "name": "Garbage in Indiranagar residential area",
        "lat": 12.9716,
        "lon": 77.6412,
        "description": "Household waste bags piled up on street",
        "expected_severity": "Medium",
        "expected_zone": "residential",
        "expected_multiplier": 1.1,
        "expected_waste": "wet",
        "notes": "Residential area with moderate waste"
    },
    {
        "name": "Overflowing bins in Jayanagar",
        "lat": 12.9250,
        "lon": 77.5838,
        "description": "Bins overflowing with garbage, spreading to road",
        "expected_severity": "High",
        "expected_zone": "residential",
        "expected_multiplier": 1.1,
        "expected_waste": "dry",
        "notes": "Overflow condition should trigger high severity"
    },
    
    # Commercial Areas - Baseline priority (1.0x multiplier)
    {
        "name": "Litter at MG Road commercial area",
        "lat": 12.9716,
        "lon": 77.6147,
        "description": "Some plastic bags and bottles near shops",
        "expected_severity": "Low",
        "expected_zone": "commercial",
        "expected_multiplier": 1.0,
        "expected_waste": "recyclable",
        "notes": "Commercial area, light litter = Low severity"
    },
    {
        "name": "Garbage at Brigade Road",
        "lat": 12.9716,
        "lon": 77.6088,
        "description": "Moderate garbage accumulation near market",
        "expected_severity": "Medium",
        "expected_zone": "commercial",
        "expected_multiplier": 1.0,
        "expected_waste": "dry",
        "notes": "Commercial area, moderate waste = Medium severity"
    },
    
    # Edge Cases
    {
        "name": "E-waste dump in Whitefield",
        "lat": 12.9698,
        "lon": 77.7500,
        "description": "Old computers, phones, and electronic waste dumped",
        "expected_severity": "High",
        "expected_zone": "commercial",
        "expected_multiplier": 1.0,
        "expected_waste": "e_waste",
        "notes": "E-waste should be classified correctly and get high priority"
    },
    {
        "name": "Clean street in Koramangala",
        "lat": 12.9279,
        "lon": 77.6271,
        "description": "Well-maintained clean street",
        "expected_severity": "Clean",
        "expected_zone": "commercial",
        "expected_multiplier": 1.0,
        "expected_waste": "other",
        "notes": "Should score very low (0-20)"
    },
    {
        "name": "Critical dump near Bangalore Palace",
        "lat": 12.9983,
        "lon": 77.5924,
        "description": "EMERGENCY! Massive open dump, hazardous materials, immediate action needed",
        "expected_severity": "Extreme",
        "expected_zone": "eco",
        "expected_multiplier": 1.3,
        "expected_waste": "hazardous",
        "notes": "Multiple risk factors: open dump + hazardous + urgent keywords"
    },
]

def test_bangalore_scenario(scenario: Dict, use_generated_image: bool = True) -> Dict:
    """Test a single Bangalore scenario"""
    print(f"\n{'='*80}")
    print(f"Testing: {scenario['name']}")
    print(f"Location: ({scenario['lat']}, {scenario['lon']})")
    print(f"{'='*80}")
    
    # Use a test image (in real scenario, would use actual garbage photos)
    test_image_path = "ai_service/test_images/moderate_garbage_test_1767345419337.png"
    
    # Check if image exists
    if not os.path.exists(test_image_path):
        # Try alternative paths
        alt_paths = [
            "C:/Users/shreeram/.gemini/antigravity/brain/81378738-d743-4450-a4bf-de29f5fc06ea/moderate_garbage_test_1767345419337.png",
            "ai_service/test_images/clean_street_test_1767345400430.png"
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                test_image_path = alt_path
                break
    
    if not os.path.exists(test_image_path):
        print(f"⚠️  No test image found, skipping...")
        return {"error": "No test image available"}
    
    try:
        # Call AI service
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'lat': scenario['lat'],
                'lon': scenario['lon'],
                'description': scenario['description'],
                'upvote_count': 0
            }
            
            start_time = time.time()
            response = requests.post(
                f"{AI_SERVICE_URL}/analyze-severity",
                files=files,
                data=data,
                timeout=20
            )
            inference_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            return {"error": f"HTTP {response.status_code}"}
        
        result = response.json()
        
        # Extract results
        severity_score = result.get('severity_score')
        severity_category = result.get('severity_category')
        location_context = result.get('location_context', {})
        location_multiplier = result.get('location_multiplier', 1.0)
        zone_type = result.get('zone_type', 'unknown')
        waste_classification = result.get('waste_classification', {})
        waste_type = waste_classification.get('primary_type', 'other')
        
        # Print results
        print(f"\n📊 ACTUAL RESULTS:")
        print(f"   Severity: {severity_score}/100 ({severity_category})")
        print(f"   Location: {zone_type} zone, {location_multiplier}x multiplier")
        print(f"   Waste Type: {waste_type}")
        
        print(f"\n🎯 EXPECTED RESULTS:")
        print(f"   Severity: {scenario['expected_severity']}")
        print(f"   Location: {scenario['expected_zone']} zone, {scenario['expected_multiplier']}x multiplier")
        print(f"   Waste Type: {scenario['expected_waste']}")
        
        # Validation
        severity_match = severity_category == scenario['expected_severity']
        zone_match = zone_type == scenario['expected_zone']
        multiplier_close = abs(location_multiplier - scenario['expected_multiplier']) < 0.2
        waste_match = waste_type == scenario['expected_waste']
        
        print(f"\n✅ VALIDATION:")
        print(f"   Severity: {'✅ MATCH' if severity_match else '❌ MISMATCH'}")
        print(f"   Zone: {'✅ MATCH' if zone_match else '❌ MISMATCH'}")
        print(f"   Multiplier: {'✅ CLOSE' if multiplier_close else '❌ OFF'}")
        print(f"   Waste Type: {'✅ MATCH' if waste_match else '❌ MISMATCH'}")
        
        # Show nearby locations
        if location_context.get('nearby_locations'):
            print(f"\n📍 NEARBY LOCATIONS:")
            for loc in location_context['nearby_locations'][:3]:
                print(f"   • {loc['name']} ({loc['type']}, {loc['distance_m']}m)")
        
        print(f"\n💡 NOTES: {scenario['notes']}")
        print(f"⏱️  Inference Time: {inference_time:.2f}s")
        
        return {
            "scenario": scenario['name'],
            "actual_severity": severity_category,
            "expected_severity": scenario['expected_severity'],
            "severity_match": severity_match,
            "actual_zone": zone_type,
            "expected_zone": scenario['expected_zone'],
            "zone_match": zone_match,
            "actual_multiplier": location_multiplier,
            "expected_multiplier": scenario['expected_multiplier'],
            "multiplier_close": multiplier_close,
            "actual_waste": waste_type,
            "expected_waste": scenario['expected_waste'],
            "waste_match": waste_match,
            "severity_score": severity_score,
            "inference_time": inference_time,
            "nearby_locations": location_context.get('nearby_locations', []),
            "full_result": result
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

def analyze_bangalore_results(results: List[Dict]) -> Dict:
    """Analyze results and identify improvement areas"""
    print(f"\n{'='*80}")
    print("BANGALORE LOCATION TEST - ANALYSIS")
    print(f"{'='*80}")
    
    successful = [r for r in results if 'error' not in r]
    
    if not successful:
        print("❌ No successful tests")
        return {}
    
    # Calculate accuracies
    severity_accuracy = sum(1 for r in successful if r.get('severity_match')) / len(successful) * 100
    zone_accuracy = sum(1 for r in successful if r.get('zone_match')) / len(successful) * 100
    multiplier_accuracy = sum(1 for r in successful if r.get('multiplier_close')) / len(successful) * 100
    waste_accuracy = sum(1 for r in successful if r.get('waste_match')) / len(successful) * 100
    
    print(f"\n📈 ACCURACY METRICS:")
    print(f"   Severity Classification: {severity_accuracy:.1f}% ({sum(1 for r in successful if r.get('severity_match'))}/{len(successful)})")
    print(f"   Zone Detection: {zone_accuracy:.1f}% ({sum(1 for r in successful if r.get('zone_match'))}/{len(successful)})")
    print(f"   Location Multiplier: {multiplier_accuracy:.1f}% ({sum(1 for r in successful if r.get('multiplier_close'))}/{len(successful)})")
    print(f"   Waste Classification: {waste_accuracy:.1f}% ({sum(1 for r in successful if r.get('waste_match'))}/{len(successful)})")
    
    # Identify problem areas
    print(f"\n🔍 PROBLEM AREAS:")
    
    severity_mismatches = [r for r in successful if not r.get('severity_match')]
    if severity_mismatches:
        print(f"\n   Severity Mismatches ({len(severity_mismatches)}):")
        for r in severity_mismatches[:5]:
            print(f"   • {r['scenario']}")
            print(f"     Expected: {r['expected_severity']}, Got: {r['actual_severity']}")
    
    zone_mismatches = [r for r in successful if not r.get('zone_match')]
    if zone_mismatches:
        print(f"\n   Zone Detection Issues ({len(zone_mismatches)}):")
        for r in zone_mismatches[:5]:
            print(f"   • {r['scenario']}")
            print(f"     Expected: {r['expected_zone']}, Got: {r['actual_zone']}")
    
    waste_mismatches = [r for r in successful if not r.get('waste_match')]
    if waste_mismatches:
        print(f"\n   Waste Classification Issues ({len(waste_mismatches)}):")
        for r in waste_mismatches[:5]:
            print(f"   • {r['scenario']}")
            print(f"     Expected: {r['expected_waste']}, Got: {r['actual_waste']}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if severity_accuracy < 70:
        print("   ⚠️  Severity accuracy below 70%")
        if zone_accuracy > 80:
            print("   → Location detection is good, but severity weights may need adjustment")
        else:
            print("   → Both location and severity need improvement")
    
    if zone_accuracy < 60:
        print("   ⚠️  Zone detection accuracy below 60%")
        print("   → Check OpenStreetMap API connectivity")
        print("   → Verify Bangalore coordinates have proper POI data")
    
    if waste_accuracy < 60:
        print("   ⚠️  Waste classification accuracy below 60%")
        print("   → Add more keyword mappings for waste types")
        print("   → Improve COCO class to waste type mapping")
    
    if severity_accuracy >= 70 and zone_accuracy >= 60 and waste_accuracy >= 60:
        print("   ✅ Overall performance is good!")
        print("   → Continue monitoring with real-world data")
    
    # Save results
    output = {
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Bangalore, India",
        "scenarios_tested": len(BANGALORE_TEST_SCENARIOS),
        "successful_tests": len(successful),
        "accuracy": {
            "severity": severity_accuracy,
            "zone": zone_accuracy,
            "multiplier": multiplier_accuracy,
            "waste": waste_accuracy
        },
        "results": results
    }
    
    with open("bangalore_test_results.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to: bangalore_test_results.json")
    
    return output

def main():
    """Run Bangalore location tests"""
    print("="*80)
    print("BANGALORE LOCATION-BASED MODEL TESTING")
    print("="*80)
    print(f"\nTesting {len(BANGALORE_TEST_SCENARIOS)} real Bangalore locations...")
    
    # Check AI service
    try:
        health = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✅ AI Service is running")
        else:
            print("❌ AI Service not healthy")
            return
    except:
        print("❌ Cannot connect to AI Service")
        print("   Start with: docker-compose up ai_service")
        return
    
    # Run tests
    results = []
    for scenario in BANGALORE_TEST_SCENARIOS:
        result = test_bangalore_scenario(scenario)
        results.append(result)
        time.sleep(1)  # Rate limiting
    
    # Analyze
    analysis = analyze_bangalore_results(results)
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
