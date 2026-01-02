"""
Weight Tuning Configuration for Parent Model
Adjust these weights based on test results to optimize severity scoring
"""

# Current weight configuration
CURRENT_WEIGHTS = {
    'image_analysis': 0.40,     # YOLO + Scene classification
    'location_context': 0.25,   # Proximity to sensitive areas
    'text_sentiment': 0.20,     # NLP urgency/emotion analysis
    'social_signals': 0.10,     # Upvote count
    'risk_factors': 0.05        # Overflow, open dump detection
}

# Image analysis sub-weights (within 40%)
CURRENT_IMAGE_SUB_WEIGHTS = {
    'coverage_area': 0.375,     # 15% of total (40% * 0.375)
    'scene_dirtiness': 0.375,   # 15% of total
    'object_count': 0.25        # 10% of total
}

# Location priority multipliers
CURRENT_LOCATION_MULTIPLIERS = {
    'school': 1.5,
    'kindergarten': 1.5,
    'college': 1.4,
    'university': 1.4,
    'hospital': 1.4,
    'clinic': 1.4,
    'doctors': 1.4,
    'pharmacy': 1.3,
    'park': 1.3,
    'nature_reserve': 1.3,
    'playground': 1.3,
    'residential': 1.1,
    'apartments': 1.1,
    'commercial': 1.0,
    'industrial': 0.9,
}

# Text urgency boost values
CURRENT_TEXT_BOOSTS = {
    'critical': 15,   # Added to final score
    'high': 10,
    'medium': 5,
    'low': 0
}

# ============================================================================
# TUNING RECOMMENDATIONS BASED ON TEST RESULTS
# ============================================================================

# Scenario 1: If image analysis is too dominant (avg > 70)
TUNED_WEIGHTS_SCENARIO_1 = {
    'image_analysis': 0.35,     # Reduced from 0.40
    'location_context': 0.28,   # Increased from 0.25
    'text_sentiment': 0.22,     # Increased from 0.20
    'social_signals': 0.10,
    'risk_factors': 0.05
}

# Scenario 2: If location context is causing over-prioritization
TUNED_WEIGHTS_SCENARIO_2 = {
    'image_analysis': 0.45,     # Increased from 0.40
    'location_context': 0.20,   # Reduced from 0.25
    'text_sentiment': 0.20,
    'social_signals': 0.10,
    'risk_factors': 0.05
}

# Scenario 3: If text sentiment is too influential
TUNED_WEIGHTS_SCENARIO_3 = {
    'image_analysis': 0.45,     # Increased from 0.40
    'location_context': 0.25,
    'text_sentiment': 0.15,     # Reduced from 0.20
    'social_signals': 0.10,
    'risk_factors': 0.05
}

# Scenario 4: Balanced approach (if current weights are causing issues)
TUNED_WEIGHTS_BALANCED = {
    'image_analysis': 0.38,
    'location_context': 0.23,
    'text_sentiment': 0.18,
    'social_signals': 0.12,     # Increased social validation
    'risk_factors': 0.09        # Increased risk detection
}

# ============================================================================
# SEVERITY CATEGORY THRESHOLDS
# ============================================================================

# Current thresholds
CURRENT_THRESHOLDS = {
    'Clean': (0, 20),
    'Low': (21, 40),
    'Medium': (41, 60),
    'High': (61, 80),
    'Extreme': (81, 100)
}

# Alternative thresholds (if categories are too strict/lenient)
TUNED_THRESHOLDS_STRICTER = {
    'Clean': (0, 15),
    'Low': (16, 35),
    'Medium': (36, 55),
    'High': (56, 75),
    'Extreme': (76, 100)
}

TUNED_THRESHOLDS_LENIENT = {
    'Clean': (0, 25),
    'Low': (26, 45),
    'Medium': (46, 65),
    'High': (66, 85),
    'Extreme': (86, 100)
}

# ============================================================================
# HOW TO APPLY TUNED WEIGHTS
# ============================================================================

"""
To apply tuned weights:

1. Analyze test results from test_parent_model.py
2. Identify which scenario best matches the issues
3. Update ai_service/severity_scorer.py:
   
   class SeverityScorer:
       WEIGHTS = TUNED_WEIGHTS_SCENARIO_X  # Replace with chosen scenario
       
4. Restart AI service:
   docker-compose restart ai_service
   
5. Re-run tests:
   python test_parent_model.py
   
6. Compare accuracy improvements
"""

# ============================================================================
# PERFORMANCE TARGETS
# ============================================================================

PERFORMANCE_TARGETS = {
    'severity_accuracy': 75,        # Minimum 75% accuracy
    'waste_classification_accuracy': 65,  # Minimum 65% accuracy
    'avg_inference_time': 10,       # Maximum 10 seconds
    'false_positive_rate': 15,      # Maximum 15% false positives
    'false_negative_rate': 10       # Maximum 10% false negatives
}

# ============================================================================
# TESTING GUIDELINES
# ============================================================================

TESTING_GUIDELINES = """
1. Test with at least 20 diverse images
2. Include edge cases:
   - Very clean areas (should score 0-20)
   - Extreme dumps (should score 80-100)
   - Mixed waste types
   - Different locations (school, hospital, commercial)
   - Various urgency levels in descriptions

3. Monitor component scores:
   - No single component should dominate (>80)
   - All components should contribute meaningfully
   - Location multiplier should amplify, not override

4. Validate waste classification:
   - Hazardous waste must be flagged correctly
   - Wet/dry/recyclable should be distinguishable
   - Mixed waste should be identified

5. Check explanations:
   - Should mention all relevant factors
   - Should be clear and actionable
   - Should justify the severity score
"""
