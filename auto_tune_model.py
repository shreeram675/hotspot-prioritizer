"""
Auto-Tuning Script for Model Improvement
Analyzes test results and automatically suggests/applies weight adjustments
"""
import json
import os
from typing import Dict, List

def load_test_results(filename: str = "bangalore_test_results.json") -> Dict:
    """Load test results from JSON file"""
    if not os.path.exists(filename):
        print(f"❌ Results file not found: {filename}")
        print("   Run test_bangalore_locations.py first")
        return None
    
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_severity_patterns(results: List[Dict]) -> Dict:
    """Analyze severity classification patterns to identify issues"""
    patterns = {
        'over_scoring': [],  # Actual > Expected
        'under_scoring': [],  # Actual < Expected
        'correct': []
    }
    
    severity_order = ['Clean', 'Low', 'Medium', 'High', 'Extreme']
    
    for r in results:
        if 'error' in r:
            continue
        
        actual = r.get('actual_severity')
        expected = r.get('expected_severity')
        
        if actual == expected:
            patterns['correct'].append(r)
        else:
            actual_idx = severity_order.index(actual) if actual in severity_order else -1
            expected_idx = severity_order.index(expected) if expected in severity_order else -1
            
            if actual_idx > expected_idx:
                patterns['over_scoring'].append(r)
            else:
                patterns['under_scoring'].append(r)
    
    return patterns

def generate_weight_recommendations(data: Dict) -> Dict:
    """Generate weight adjustment recommendations based on test results"""
    results = data.get('results', [])
    accuracy = data.get('accuracy', {})
    
    recommendations = {
        'severity_weights': {},
        'location_multipliers': {},
        'text_boosts': {},
        'thresholds': {},
        'rationale': []
    }
    
    # Analyze severity patterns
    patterns = analyze_severity_patterns(results)
    
    # Current weights
    current_weights = {
        'image_analysis': 0.40,
        'location_context': 0.25,
        'text_sentiment': 0.20,
        'social_signals': 0.10,
        'risk_factors': 0.05
    }
    
    # Recommendation 1: Severity accuracy
    if accuracy.get('severity', 0) < 70:
        if len(patterns['over_scoring']) > len(patterns['under_scoring']):
            # Model is over-scoring
            recommendations['rationale'].append(
                "Model is over-scoring (predicting higher severity than expected)"
            )
            
            # Check if location multiplier is too high
            if accuracy.get('zone', 0) > 80:
                recommendations['severity_weights'] = {
                    'image_analysis': 0.45,  # Increase image weight
                    'location_context': 0.20,  # Reduce location weight
                    'text_sentiment': 0.20,
                    'social_signals': 0.10,
                    'risk_factors': 0.05
                }
                recommendations['rationale'].append(
                    "→ Reduce location_context weight from 0.25 to 0.20"
                )
                recommendations['rationale'].append(
                    "→ Increase image_analysis weight from 0.40 to 0.45"
                )
            else:
                # General over-scoring, reduce all amplifications
                recommendations['location_multipliers'] = {
                    'school': 1.3,  # Reduce from 1.5
                    'hospital': 1.2,  # Reduce from 1.4
                    'park': 1.2,  # Reduce from 1.3
                }
                recommendations['rationale'].append(
                    "→ Reduce location multipliers by ~0.2"
                )
        
        elif len(patterns['under_scoring']) > len(patterns['over_scoring']):
            # Model is under-scoring
            recommendations['rationale'].append(
                "Model is under-scoring (predicting lower severity than expected)"
            )
            
            recommendations['severity_weights'] = {
                'image_analysis': 0.35,  # Reduce image weight
                'location_context': 0.28,  # Increase location weight
                'text_sentiment': 0.22,  # Increase text weight
                'social_signals': 0.10,
                'risk_factors': 0.05
            }
            recommendations['rationale'].append(
                "→ Increase location_context weight from 0.25 to 0.28"
            )
            recommendations['rationale'].append(
                "→ Increase text_sentiment weight from 0.20 to 0.22"
            )
    
    # Recommendation 2: Zone detection
    if accuracy.get('zone', 0) < 60:
        recommendations['rationale'].append(
            "Zone detection accuracy is low (<60%)"
        )
        recommendations['rationale'].append(
            "→ Check OpenStreetMap API connectivity"
        )
        recommendations['rationale'].append(
            "→ Verify search radius (currently 500m)"
        )
    
    # Recommendation 3: Waste classification
    if accuracy.get('waste', 0) < 60:
        recommendations['rationale'].append(
            "Waste classification accuracy is low (<60%)"
        )
        recommendations['rationale'].append(
            "→ Add more keywords to waste_classifier.py"
        )
        recommendations['rationale'].append(
            "→ Improve COCO class to waste type mapping"
        )
    
    return recommendations

def apply_weight_updates(recommendations: Dict, dry_run: bool = True) -> str:
    """Generate updated severity_scorer.py with new weights"""
    
    if not recommendations.get('severity_weights'):
        return "No weight updates recommended"
    
    new_weights = recommendations['severity_weights']
    
    # Generate updated code
    updated_code = f"""
# UPDATED WEIGHTS (Auto-tuned based on Bangalore test results)
WEIGHTS = {{
    'image_analysis': {new_weights.get('image_analysis', 0.40)},
    'location_context': {new_weights.get('location_context', 0.25)},
    'text_sentiment': {new_weights.get('text_sentiment', 0.20)},
    'social_signals': {new_weights.get('social_signals', 0.10)},
    'risk_factors': {new_weights.get('risk_factors', 0.05)}
}}
"""
    
    if dry_run:
        print("\n📝 PROPOSED WEIGHT UPDATES:")
        print(updated_code)
        print("\nTo apply these changes:")
        print("1. Update ai_service/severity_scorer.py with the new WEIGHTS")
        print("2. Restart AI service: docker-compose restart ai_service")
        print("3. Re-run tests: python test_bangalore_locations.py")
    else:
        # Actually update the file
        print("⚠️  Auto-update not implemented yet (safety measure)")
        print("   Please manually update severity_scorer.py")
    
    return updated_code

def main():
    """Main auto-tuning workflow"""
    print("="*80)
    print("MODEL AUTO-TUNING BASED ON BANGALORE TEST RESULTS")
    print("="*80)
    
    # Load results
    data = load_test_results()
    if not data:
        return
    
    print(f"\n📊 Test Results Loaded:")
    print(f"   Date: {data.get('test_date')}")
    print(f"   Scenarios: {data.get('scenarios_tested')}")
    print(f"   Successful: {data.get('successful_tests')}")
    
    accuracy = data.get('accuracy', {})
    print(f"\n📈 Current Accuracy:")
    print(f"   Severity: {accuracy.get('severity', 0):.1f}%")
    print(f"   Zone: {accuracy.get('zone', 0):.1f}%")
    print(f"   Multiplier: {accuracy.get('multiplier', 0):.1f}%")
    print(f"   Waste: {accuracy.get('waste', 0):.1f}%")
    
    # Generate recommendations
    print(f"\n🔍 Analyzing patterns...")
    recommendations = generate_weight_recommendations(data)
    
    print(f"\n💡 RECOMMENDATIONS:")
    if recommendations['rationale']:
        for i, rec in enumerate(recommendations['rationale'], 1):
            print(f"   {i}. {rec}")
    else:
        print("   ✅ No major issues detected!")
        print("   Current configuration is performing well.")
    
    # Show proposed updates
    if recommendations.get('severity_weights'):
        apply_weight_updates(recommendations, dry_run=True)
    
    # Save recommendations
    with open("tuning_recommendations.json", 'w') as f:
        json.dump(recommendations, f, indent=2)
    
    print(f"\n💾 Recommendations saved to: tuning_recommendations.json")
    print("\n✅ Auto-tuning analysis complete!")

if __name__ == "__main__":
    main()
