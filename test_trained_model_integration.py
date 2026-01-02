"""
Test Script: Verify Trained Model Integration with Child Models
Tests the complete pipeline from child models → parent model → calibrated output
"""
import sys
import os

# Add ai_service to path
sys.path.insert(0, 'ai_service')

def test_model_loading():
    """Test 1: Check if trained model loads correctly"""
    print("="*80)
    print("TEST 1: Model Loading")
    print("="*80)
    
    from hybrid_severity_scorer import HybridSeverityScorer
    
    info = HybridSeverityScorer.get_model_info()
    
    print(f"\n📦 Model Info:")
    print(f"   Loaded: {info.get('loaded')}")
    print(f"   Path: {info.get('path')}")
    print(f"   Type: {info.get('model_type', 'N/A')}")
    print(f"   Features: {info.get('feature_count', 'N/A')}")
    
    if info.get('loaded'):
        print("\n✅ Model loaded successfully!")
        return True
    else:
        print(f"\n❌ Model failed to load: {info.get('message')}")
        return False

def test_calibration_function():
    """Test 2: Verify calibration function works correctly"""
    print("\n" + "="*80)
    print("TEST 2: Calibration Function")
    print("="*80)
    
    from trained_model_loader import calibrate_severity_score
    
    test_cases = [
        (20, 20, "Low severity - no change"),
        (35, 35, "Low severity - no change"),
        (50, 57, "Medium severity - 15% boost"),
        (65, 74, "Medium severity - 15% boost"),
        (75, 93, "High severity - 25% boost"),
        (85, 100, "High severity - capped at 100"),
        (95, 100, "Very high - capped at 100"),
    ]
    
    print("\n📊 Calibration Test Cases:")
    print(f"{'Raw Score':<12} {'Expected':<12} {'Actual':<12} {'Status':<10} {'Description'}")
    print("-" * 80)
    
    all_passed = True
    for raw, expected, desc in test_cases:
        actual = calibrate_severity_score(raw)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        if actual != expected:
            all_passed = False
        print(f"{raw:<12} {expected:<12} {actual:<12} {status:<10} {desc}")
    
    if all_passed:
        print("\n✅ All calibration tests passed!")
    else:
        print("\n❌ Some calibration tests failed!")
    
    return all_passed

def test_feature_preparation():
    """Test 3: Verify feature vector preparation"""
    print("\n" + "="*80)
    print("TEST 3: Feature Vector Preparation")
    print("="*80)
    
    from trained_model_loader import prepare_features_for_model
    
    # Mock child model outputs
    object_detection = {
        'object_count': 12,
        'coverage_area': 0.25,
        'density': 5.2,
        'has_overflow': False,
        'is_open_dump': False,
        'bin_detected': True
    }
    
    scene_classification = {
        'dirtiness_score': 0.65,
        'confidence': 0.82,
        'dirty_indicators': 0.7,
        'clean_indicators': 0.3
    }
    
    location_context = {
        'priority_multiplier': 1.5,
        'zone_type': 'educational'
    }
    
    text_analysis = {
        'sentiment_score': 0.6,
        'severity_boost': 10,
        'urgency_level': 'high'
    }
    
    # Prepare features
    features, full_dict = prepare_features_for_model(
        object_detection,
        scene_classification,
        location_context,
        text_analysis,
        upvote_count=5
    )
    
    print(f"\n📊 Feature Vector (For Model):")
    print(f"   Shape: {features.shape}")
    print(f"   Expected: (1, 7)")
    
    if features.shape[1] == 7:
        print(f"   ✅ Correct feature count for model (7)!")
    else:
        print(f"   ❌ Feature count mismatch via map (got {features.shape[1]}, expected 7)!")
        return False

    print(f"\n📊 Full Feature Dictionary (For Frontend):")
    feature_count = len(full_dict)
    print(f"   Count: {feature_count}")
    print(f"   Expected: 21")
    
    if feature_count == 21:
        print(f"   ✅ All 21 features present!")
    else:
        print(f"   ❌ Feature count mismatch for display (got {feature_count}, expected 21)!")
        print(f"   Keys missing: {set(['object_count', 'coverage_area', 'dirtiness_score', 'location_multiplier']).difference(full_dict.keys())}")
        return False
    
    print(f"\n📋 Model Input Values (7 mapped features):")
    model_labels = [
        "1. Object Count", "2. Coverage Area", "3. Dirtiness Score", 
        "4. Location Multiplier", "5. Text Severity", "6. Social Score", "7. Risk Factor"
    ]
    for i, (name, value) in enumerate(zip(model_labels, features[0])):
        print(f"   {name:<30} = {value:.3f}")
    
    print("\n✅ Feature preparation successful!")
    return True

def test_end_to_end_prediction():
    """Test 4: End-to-end prediction with child models"""
    print("\n" + "="*80)
    print("TEST 4: End-to-End Prediction")
    print("="*80)
    
    from hybrid_severity_scorer import HybridSeverityScorer
    
    # Test scenarios
    scenarios = [
        {
            "name": "Moderate Garbage Near School",
            "object_detection": {
                'object_count': 15,
                'coverage_area': 0.30,
                'density': 6.5,
                'has_overflow': False,
                'is_open_dump': False,
                'bin_detected': True
            },
            "scene_classification": {
                'dirtiness_score': 0.65,
                'confidence': 0.85,
                'dirty_indicators': 0.7,
                'clean_indicators': 0.3
            },
            "location_context": {
                'priority_multiplier': 1.5,
                'zone_type': 'educational',
                'nearby_locations': [{'type': 'school', 'name': 'ABC School', 'distance_m': 50}]
            },
            "text_analysis": {
                'sentiment_score': 0.6,
                'severity_boost': 10,
                'urgency_level': 'high',
                'keywords': ['garbage', 'school']
            },
            "upvote_count": 3
        },
        {
            "name": "Light Litter in Commercial Area",
            "object_detection": {
                'object_count': 5,
                'coverage_area': 0.08,
                'density': 2.0,
                'has_overflow': False,
                'is_open_dump': False,
                'bin_detected': False
            },
            "scene_classification": {
                'dirtiness_score': 0.25,
                'confidence': 0.75,
                'dirty_indicators': 0.3,
                'clean_indicators': 0.7
            },
            "location_context": None,
            "text_analysis": None,
            "upvote_count": 0
        }
    ]
    
    print("\n🧪 Testing Scenarios:\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─'*80}")
        print(f"Scenario {i}: {scenario['name']}")
        print(f"{'─'*80}")
        
        result = HybridSeverityScorer.calculate_severity(
            scenario['object_detection'],
            scenario['scene_classification'],
            scenario.get('location_context'),
            scenario.get('text_analysis'),
            scenario.get('upvote_count', 0)
        )
        
        print(f"\n📊 Results:")
        print(f"   Prediction Method: {result.get('prediction_method')}")
        
        if result.get('prediction_method') == 'trained_model':
            print(f"   Model Type: {result.get('model_type')}")
            print(f"   Raw Score: {result.get('raw_score', 'N/A')}")
            print(f"   Calibrated Score: {result.get('severity_score')}")
            print(f"   Calibration Applied: {result.get('calibrated', False)}")
            print(f"   Rule-Based Score: {result.get('rule_based_score')} (for comparison)")
            
            feats = result.get('model_input_features', {})
            print(f"   Frontend Features Count: {len(feats)} (Expected: 21)")
            if len(feats) > 0:
                print(f"   Sample Feature: object_count={feats.get('object_count')}")
        else:
            print(f"   Score: {result.get('severity_score')}")
        
        print(f"   Category: {result.get('severity_category')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        print(f"   Zone: {result.get('zone_type', 'N/A')}")
        print(f"   Location Multiplier: {result.get('location_multiplier', 'N/A')}")
    
    print("\n✅ End-to-end prediction successful!")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("TRAINED MODEL INTEGRATION TEST SUITE")
    print("="*80)
    print("\nTesting integration of parent_severity_model.pkl with child models\n")
    
    results = []
    
    # Test 1: Model Loading
    results.append(("Model Loading", test_model_loading()))
    
    # Test 2: Calibration Function
    results.append(("Calibration Function", test_calibration_function()))
    
    # Test 3: Feature Preparation
    results.append(("Feature Preparation", test_feature_preparation()))
    
    # Test 4: End-to-End Prediction
    results.append(("End-to-End Prediction", test_end_to_end_prediction()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name:<30} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n📊 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Model integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")

if __name__ == "__main__":
    main()
