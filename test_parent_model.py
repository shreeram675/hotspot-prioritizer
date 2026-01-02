"""
Comprehensive Test Suite for Parent Model Validation
Tests the complete AI severity analysis pipeline with sample images
"""
import requests
import json
import os
from typing import List, Dict
import time

# Configuration
AI_SERVICE_URL = "http://localhost:8001"
TEST_IMAGES_DIR = "ai_service/test_images"
RESULTS_FILE = "model_test_results.json"

# Test scenarios with expected outcomes
TEST_SCENARIOS = [
    {
        "name": "Clean Street",
        "image": "clean_street.jpg",
        "description": "Clean and well-maintained street",
        "lat": 12.9716,
        "lon": 77.5946,
        "expected_severity": "Clean",
        "expected_waste_type": "other"
    },
    {
        "name": "Light Litter",
        "image": "light_litter.jpg",
        "description": "Few plastic bottles on sidewalk",
        "lat": 12.9352,
        "lon": 77.6245,
        "expected_severity": "Low",
        "expected_waste_type": "recyclable"
    },
    {
        "name": "Moderate Garbage",
        "image": "moderate_garbage.jpg",
        "description": "Some garbage accumulation",
        "lat": 12.9500,
        "lon": 77.6000,
        "expected_severity": "Medium",
        "expected_waste_type": "dry"
    },
    {
        "name": "Heavy Garbage",
        "image": "heavy_garbage.jpg",
        "description": "Significant waste pile",
        "lat": 12.9400,
        "lon": 77.6100,
        "expected_severity": "High",
        "expected_waste_type": "dry"
    },
    {
        "name": "Garbage Near School",
        "image": "moderate_garbage.jpg",
        "description": "Garbage accumulation",
        "lat": 12.9716,  # Near school coordinates
        "lon": 77.5946,
        "expected_severity": "High",  # Should be elevated due to location
        "expected_waste_type": "dry"
    },
    {
        "name": "Urgent Garbage Report",
        "image": "moderate_garbage.jpg",
        "description": "URGENT! Overflowing garbage bins, health hazard!",
        "lat": 12.9500,
        "lon": 77.6000,
        "expected_severity": "High",  # Should be elevated due to urgency
        "expected_waste_type": "dry"
    },
    {
        "name": "Food Waste",
        "image": "food_waste.jpg",
        "description": "Rotting food waste and organic matter",
        "lat": 12.9400,
        "lon": 77.6100,
        "expected_severity": "Medium",
        "expected_waste_type": "wet"
    },
    {
        "name": "Plastic Bottles",
        "image": "plastic_bottles.jpg",
        "description": "Many plastic bottles scattered",
        "lat": 12.9300,
        "lon": 77.6200,
        "expected_severity": "Medium",
        "expected_waste_type": "recyclable"
    },
    {
        "name": "Hazardous Waste",
        "image": "hazardous_waste.jpg",
        "description": "Medical waste and syringes found",
        "lat": 12.9600,
        "lon": 77.5800,
        "expected_severity": "Extreme",
        "expected_waste_type": "hazardous"
    },
    {
        "name": "E-Waste Dump",
        "image": "e_waste.jpg",
        "description": "Old electronics and batteries dumped",
        "lat": 12.9450,
        "lon": 77.6050,
        "expected_severity": "High",
        "expected_waste_type": "e_waste"
    }
]

def test_single_image(scenario: Dict) -> Dict:
    """Test a single image scenario"""
    print(f"\n{'='*60}")
    print(f"Testing: {scenario['name']}")
    print(f"{'='*60}")
    
    image_path = os.path.join(TEST_IMAGES_DIR, scenario['image'])
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"⚠️  Image not found: {image_path}")
        print(f"   Using placeholder for testing...")
        # Use any available image as placeholder
        available_images = [f for f in os.listdir(TEST_IMAGES_DIR) if f.endswith(('.jpg', '.png'))]
        if available_images:
            image_path = os.path.join(TEST_IMAGES_DIR, available_images[0])
        else:
            return {"error": "No test images available"}
    
    try:
        # Prepare request
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'lat': scenario.get('lat'),
                'lon': scenario.get('lon'),
                'description': scenario.get('description', ''),
                'upvote_count': scenario.get('upvote_count', 0)
            }
            
            # Call AI service
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
            print(f"   Response: {response.text}")
            return {"error": f"HTTP {response.status_code}"}
        
        result = response.json()
        
        # Extract key metrics
        severity_score = result.get('severity_score')
        severity_category = result.get('severity_category')
        
        # Component scores
        component_scores = result.get('component_scores', {})
        
        # Location context
        location_context = result.get('location_context', {})
        location_multiplier = result.get('location_multiplier', 1.0)
        zone_type = result.get('zone_type', 'commercial')
        
        # Text analysis
        text_analysis = result.get('text_analysis', {})
        urgency_level = text_analysis.get('urgency_level', 'low')
        
        # Waste classification
        waste_classification = result.get('waste_classification', {})
        waste_type = waste_classification.get('primary_type', 'other')
        
        # Object detection
        obj_detection = result.get('object_detection', {})
        object_count = obj_detection.get('object_count', 0)
        
        # Print results
        print(f"\n📊 RESULTS:")
        print(f"   Severity Score: {severity_score}/100")
        print(f"   Severity Category: {severity_category}")
        print(f"   Expected: {scenario['expected_severity']}")
        
        # Check if result matches expectation
        match = severity_category == scenario['expected_severity']
        if match:
            print(f"   ✅ MATCH!")
        else:
            print(f"   ⚠️  MISMATCH (Expected: {scenario['expected_severity']})")
        
        print(f"\n🔍 COMPONENT BREAKDOWN:")
        print(f"   Image Analysis: {component_scores.get('image_analysis_score', 0):.1f}")
        print(f"   Location Context: {component_scores.get('location_context_score', 0):.1f} (Multiplier: {location_multiplier}x, Zone: {zone_type})")
        print(f"   Text Sentiment: {component_scores.get('text_sentiment_score', 0):.1f} (Urgency: {urgency_level})")
        print(f"   Social Signals: {component_scores.get('social_signals_score', 0):.1f}")
        print(f"   Risk Factors: {component_scores.get('risk_factors_score', 0):.1f}")
        
        print(f"\n🗑️  WASTE CLASSIFICATION:")
        print(f"   Type: {waste_type}")
        print(f"   Expected: {scenario['expected_waste_type']}")
        waste_match = waste_type == scenario['expected_waste_type']
        if waste_match:
            print(f"   ✅ MATCH!")
        else:
            print(f"   ⚠️  MISMATCH")
        
        if waste_classification.get('waste_composition'):
            print(f"   Composition: {waste_classification['waste_composition']}")
        
        print(f"\n📝 EXPLANATION:")
        print(f"   {result.get('explanation', 'N/A')}")
        
        print(f"\n⏱️  Inference Time: {inference_time:.2f}s")
        
        # Return structured result
        return {
            "scenario": scenario['name'],
            "severity_score": severity_score,
            "severity_category": severity_category,
            "expected_severity": scenario['expected_severity'],
            "severity_match": match,
            "waste_type": waste_type,
            "expected_waste_type": scenario['expected_waste_type'],
            "waste_match": waste_match,
            "component_scores": component_scores,
            "location_multiplier": location_multiplier,
            "zone_type": zone_type,
            "urgency_level": urgency_level,
            "object_count": object_count,
            "inference_time": inference_time,
            "full_result": result
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

def analyze_results(results: List[Dict]) -> Dict:
    """Analyze test results and provide recommendations"""
    print(f"\n{'='*60}")
    print("OVERALL ANALYSIS")
    print(f"{'='*60}")
    
    successful_tests = [r for r in results if 'error' not in r]
    total_tests = len(results)
    
    if not successful_tests:
        print("❌ No successful tests to analyze")
        return {}
    
    # Calculate accuracy
    severity_matches = sum(1 for r in successful_tests if r.get('severity_match'))
    waste_matches = sum(1 for r in successful_tests if r.get('waste_match'))
    
    severity_accuracy = (severity_matches / len(successful_tests)) * 100
    waste_accuracy = (waste_matches / len(successful_tests)) * 100
    
    print(f"\n📈 ACCURACY:")
    print(f"   Severity Classification: {severity_accuracy:.1f}% ({severity_matches}/{len(successful_tests)})")
    print(f"   Waste Type Classification: {waste_accuracy:.1f}% ({waste_matches}/{len(successful_tests)})")
    
    # Average component scores
    avg_scores = {
        'image': sum(r.get('component_scores', {}).get('image_analysis_score', 0) for r in successful_tests) / len(successful_tests),
        'location': sum(r.get('component_scores', {}).get('location_context_score', 0) for r in successful_tests) / len(successful_tests),
        'text': sum(r.get('component_scores', {}).get('text_sentiment_score', 0) for r in successful_tests) / len(successful_tests),
        'social': sum(r.get('component_scores', {}).get('social_signals_score', 0) for r in successful_tests) / len(successful_tests),
        'risk': sum(r.get('component_scores', {}).get('risk_factors_score', 0) for r in successful_tests) / len(successful_tests)
    }
    
    print(f"\n📊 AVERAGE COMPONENT SCORES:")
    print(f"   Image Analysis: {avg_scores['image']:.1f}")
    print(f"   Location Context: {avg_scores['location']:.1f}")
    print(f"   Text Sentiment: {avg_scores['text']:.1f}")
    print(f"   Social Signals: {avg_scores['social']:.1f}")
    print(f"   Risk Factors: {avg_scores['risk']:.1f}")
    
    # Average inference time
    avg_inference_time = sum(r.get('inference_time', 0) for r in successful_tests) / len(successful_tests)
    print(f"\n⏱️  AVERAGE INFERENCE TIME: {avg_inference_time:.2f}s")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if severity_accuracy < 70:
        print("   ⚠️  Severity accuracy below 70% - Consider tuning weights")
        
        # Analyze which component is most predictive
        if avg_scores['image'] < 30:
            print("   → Image analysis scores are low - May need better object detection")
        if avg_scores['location'] > 70 and severity_accuracy < 70:
            print("   → Location context weight might be too high")
        if avg_scores['text'] > 70 and severity_accuracy < 70:
            print("   → Text sentiment weight might be too high")
    else:
        print("   ✅ Severity accuracy is good!")
    
    if waste_accuracy < 60:
        print("   ⚠️  Waste classification accuracy below 60% - May need more training data")
    else:
        print("   ✅ Waste classification accuracy is good!")
    
    if avg_inference_time > 10:
        print("   ⚠️  Inference time is high - Consider optimization")
    else:
        print("   ✅ Inference time is acceptable!")
    
    return {
        "total_tests": total_tests,
        "successful_tests": len(successful_tests),
        "severity_accuracy": severity_accuracy,
        "waste_accuracy": waste_accuracy,
        "average_scores": avg_scores,
        "average_inference_time": avg_inference_time
    }

def main():
    """Run comprehensive test suite"""
    print("="*60)
    print("PARENT MODEL COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"\nTesting {len(TEST_SCENARIOS)} scenarios...")
    print(f"AI Service: {AI_SERVICE_URL}")
    
    # Check if AI service is running
    try:
        health_response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ AI Service is running")
            models = health_response.json().get('models', {})
            print(f"   Models loaded: {', '.join(models.keys())}")
        else:
            print("❌ AI Service health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to AI Service: {e}")
        print(f"   Please start the service with: docker-compose up ai_service")
        return
    
    # Run tests
    results = []
    for scenario in TEST_SCENARIOS:
        result = test_single_image(scenario)
        results.append(result)
        time.sleep(0.5)  # Small delay between tests
    
    # Analyze results
    analysis = analyze_results(results)
    
    # Save results to file
    output = {
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scenarios_tested": len(TEST_SCENARIOS),
        "results": results,
        "analysis": analysis
    }
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to: {RESULTS_FILE}")
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
