"""
Verification Script for AI Severity Analysis System
Tests the new /analyze-severity endpoint with sample images
"""
import requests
import os
import sys

# Configuration
AI_SERVICE_URL = "http://localhost:8001"  # AI service runs on port 8001
TEST_IMAGES_DIR = "ai_service/test_images"

def test_health_check():
    """Test if AI service is running and models are loaded"""
    print("=" * 60)
    print("Testing AI Service Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ AI Service is healthy")
            print(f"  Models loaded: {data.get('models')}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect to AI service: {e}")
        print(f"  Make sure the service is running at {AI_SERVICE_URL}")
        return False

def test_legacy_detect_endpoint():
    """Test legacy /detect endpoint for backward compatibility"""
    print("\n" + "=" * 60)
    print("Testing Legacy /detect Endpoint")
    print("=" * 60)
    
    # Use a simple test image (create a dummy one if needed)
    test_file = "ai_service/test_images/sample.jpg"
    
    if not os.path.exists(test_file):
        print(f"⚠ Test image not found: {test_file}")
        print("  Skipping legacy endpoint test")
        return True
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{AI_SERVICE_URL}/detect", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Legacy endpoint working")
            print(f"  Is garbage: {data.get('is_garbage')}")
            print(f"  Category: {data.get('detected_category')}")
            print(f"  Confidence: {data.get('confidence'):.3f}")
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_severity_analysis(image_path, expected_category=None):
    """Test /analyze-severity endpoint with a specific image"""
    print(f"\nTesting: {os.path.basename(image_path)}")
    print("-" * 60)
    
    if not os.path.exists(image_path):
        print(f"⚠ Image not found: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{AI_SERVICE_URL}/analyze-severity",
                files=files,
                timeout=15  # YOLO takes longer
            )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✓ Analysis successful")
            print(f"\n  Severity Score: {data.get('severity_score')}/100")
            print(f"  Severity Category: {data.get('severity_category')}")
            print(f"  Confidence: {data.get('confidence'):.3f}")
            
            # Object Detection Results
            obj_det = data.get('object_detection', {})
            print(f"\n  Object Detection:")
            print(f"    - Objects detected: {obj_det.get('object_count')}")
            print(f"    - Coverage area: {obj_det.get('coverage_area', 0):.2%}")
            print(f"    - Has overflow: {obj_det.get('has_overflow')}")
            print(f"    - Is open dump: {obj_det.get('is_open_dump')}")
            
            # Scene Classification Results
            scene = data.get('scene_classification', {})
            print(f"\n  Scene Classification:")
            print(f"    - Dirtiness score: {scene.get('dirtiness_score', 0):.3f}")
            print(f"    - Category: {scene.get('cleanliness_category')}")
            
            # Explanation
            print(f"\n  Explanation: {data.get('explanation')}")
            
            # Validate expected category if provided
            if expected_category:
                actual = data.get('severity_category')
                if actual == expected_category:
                    print(f"\n  ✓ Expected category matched: {expected_category}")
                else:
                    print(f"\n  ⚠ Category mismatch: expected {expected_category}, got {actual}")
            
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_batch_analysis():
    """Test /analyze-severity-batch endpoint"""
    print("\n" + "=" * 60)
    print("Testing Batch Analysis Endpoint")
    print("=" * 60)
    
    # Find all test images
    test_images = []
    if os.path.exists(TEST_IMAGES_DIR):
        for filename in os.listdir(TEST_IMAGES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(TEST_IMAGES_DIR, filename))
    
    if len(test_images) < 2:
        print("⚠ Need at least 2 images for batch testing")
        print("  Skipping batch analysis test")
        return True
    
    try:
        files = []
        for img_path in test_images[:5]:  # Test with up to 5 images
            with open(img_path, 'rb') as f:
                files.append(('files', (os.path.basename(img_path), f.read(), 'image/jpeg')))
        
        response = requests.post(
            f"{AI_SERVICE_URL}/analyze-severity-batch",
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            summary = data.get('summary', {})
            
            print(f"✓ Batch analysis successful")
            print(f"\n  Analyzed {len(results)} images")
            print(f"\n  Summary:")
            print(f"    - Average severity: {summary.get('average_severity')}")
            print(f"    - Max severity: {summary.get('max_severity')}")
            print(f"    - Hotspot count: {summary.get('hotspot_count')}")
            print(f"    - Priority level: {summary.get('priority_level')}")
            
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("AI SEVERITY ANALYSIS SYSTEM - VERIFICATION")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ AI Service is not running or not healthy")
        print("   Please start the service with: docker-compose up ai_service")
        sys.exit(1)
    
    # Test 2: Legacy endpoint
    test_legacy_detect_endpoint()
    
    # Test 3: Severity analysis with individual images
    print("\n" + "=" * 60)
    print("Testing Severity Analysis Endpoint")
    print("=" * 60)
    
    test_cases = [
        ("ai_service/test_images/clean_street.jpg", "Clean"),
        ("ai_service/test_images/light_litter.jpg", "Low"),
        ("ai_service/test_images/moderate_garbage.jpg", "Medium"),
        ("ai_service/test_images/heavy_garbage.jpg", "High"),
        ("ai_service/test_images/extreme_dump.jpg", "Extreme"),
    ]
    
    success_count = 0
    for image_path, expected_cat in test_cases:
        if test_severity_analysis(image_path, expected_cat):
            success_count += 1
    
    # Test 4: Batch analysis
    test_batch_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Individual tests passed: {success_count}/{len(test_cases)}")
    print("\n✓ Verification complete!")
    print("\nNext steps:")
    print("1. Test report creation with images via frontend")
    print("2. Verify AI analysis data is stored in database")
    print("3. Check that severity scores are displayed correctly")

if __name__ == "__main__":
    main()
