"""
Trained Model Loader for Severity Prediction
Loads and uses a pre-trained .pkl model for severity scoring
"""
import pickle
import numpy as np
from typing import Dict, Optional
import os

# Global model cache
_trained_model = None
_model_path = None

def calibrate_severity_score(score: float) -> int:
    """
    Post-prediction calibration to improve sensitivity for high-severity cases.
    
    This stretches medium & high severity ranges while keeping low scores unchanged.
    Output stays in 0-100 range.
    
    Args:
        score: Raw severity score from model (0-100)
        
    Returns:
        Calibrated severity score (0-100)
    """
    if score < 40:
        # Low severity: no adjustment
        return int(score)
    elif score < 70:
        # Medium severity: 15% boost
        return int(score * 1.15)
    else:
        # High severity: 25% boost, capped at 100
        return min(100, int(score * 1.25))

def load_trained_model(model_path: str = "ai_service/models/parent_severity_model.pkl"):
    """
    Load the trained severity prediction model from .pkl file
    
    Args:
        model_path: Path to the .pkl file containing the trained model
        
    Returns:
        Loaded model object
    """
    global _trained_model, _model_path
    
    if _trained_model is not None and _model_path == model_path:
        return _trained_model
    
    if not os.path.exists(model_path):
        print(f"⚠️  Trained model not found at: {model_path}")
        print(f"   Falling back to rule-based severity scoring")
        return None
    
    try:
        print(f"Loading trained severity model from: {model_path}")
        with open(model_path, 'rb') as f:
            _trained_model = pickle.load(f)
        _model_path = model_path
        print(f"✅ Trained model loaded successfully")
        print(f"   Model type: {type(_trained_model).__name__}")
        return _trained_model
    except Exception as e:
        print(f"❌ Error loading trained model: {e}")
        return None

def prepare_features_for_model(
    object_detection_result: Dict,
    scene_classification_result: Dict,
    location_context_result: Optional[Dict] = None,
    text_analysis_result: Optional[Dict] = None,
    upvote_count: int = 0
) -> np.ndarray:
    """
    Prepare feature vector from all model outputs for the trained model
    
    This creates a feature vector that matches what your model was trained on.
    Adjust the features based on your training data.
    
    Returns:
        numpy array of features
    """
    # Prepare full 21-feature list for frontend display
    full_features_dict = {
        # Object Detection (6)
        'object_count': object_detection_result.get('object_count', 0),
        'coverage_area': object_detection_result.get('coverage_area', 0.0),
        'density': object_detection_result.get('density', 0.0),
        'has_overflow': 1.0 if object_detection_result.get('has_overflow', False) else 0.0,
        'is_open_dump': 1.0 if object_detection_result.get('is_open_dump', False) else 0.0,
        'bin_detected': 1.0 if object_detection_result.get('bin_detected', False) else 0.0,
        
        # Scene Classification (4)
        'dirtiness_score': scene_classification_result.get('dirtiness_score', 0.0),
        'scene_confidence': scene_classification_result.get('confidence', 0.0),
        'dirty_indicators': scene_classification_result.get('dirty_indicators', 0.0),
        'clean_indicators': scene_classification_result.get('clean_indicators', 0.0),
        
        # Location Context (5)
        'location_multiplier': location_context_result.get('priority_multiplier', 1.0) if location_context_result else 1.0,
        'zone_educational': 0.0,
        'zone_healthcare': 0.0,
        'zone_eco': 0.0,
        'zone_residential': 0.0,
        
        # Text Sentiment (5)
        'sentiment_score': 0.0,
        'text_boost_normalized': 0.0,
        'urgency_critical': 0.0,
        'urgency_high': 0.0,
        'urgency_medium': 0.0,
        
        # Social Signals (1)
        'upvote_count_normalized': min(upvote_count / 100.0, 1.0)
    }

    # Fill Location One-Hot
    if location_context_result:
        zone_type = location_context_result.get('zone_type', 'commercial')
        if zone_type == 'educational': full_features_dict['zone_educational'] = 1.0
        elif zone_type == 'healthcare': full_features_dict['zone_healthcare'] = 1.0
        elif zone_type == 'eco': full_features_dict['zone_eco'] = 1.0
        elif zone_type == 'residential': full_features_dict['zone_residential'] = 1.0

    # Fill Text Features
    if text_analysis_result:
        full_features_dict['sentiment_score'] = text_analysis_result.get('sentiment_score', 0.0)
        full_features_dict['text_boost_normalized'] = text_analysis_result.get('severity_boost', 0) / 30.0
        urgency = text_analysis_result.get('urgency_level', 'low')
        if urgency == 'critical': full_features_dict['urgency_critical'] = 1.0
        elif urgency == 'high': full_features_dict['urgency_high'] = 1.0
        elif urgency == 'medium': full_features_dict['urgency_medium'] = 1.0

    # -------------------------------------------------------------------------
    # FEATURE MAPPING: 21 Inputs -> 7 Model Inputs
    # -------------------------------------------------------------------------
    # The current trained model expects a compact 7-feature vector:
    # 1. Object Count (Image)
    # 2. Coverage Area (Image)
    # 3. Dirtiness Score (Scene)
    # 4. Location Mutiplier (Context)
    # 5. Text Severity Score (Text - combined sentiment/urgency)
    # 6. Social Score (Social)
    # 7. Risk Factor (Combined overflow/dump/critical urgency)
    
    # Calculate derived features for the mapping
    text_severity_combined = full_features_dict['text_boost_normalized']
    risk_factor = max(
        full_features_dict['has_overflow'],
        full_features_dict['is_open_dump'],
        full_features_dict['urgency_critical']
    )

    model_features = [
        full_features_dict['object_count'],       # 1
        full_features_dict['coverage_area'],      # 2
        full_features_dict['dirtiness_score'],    # 3
        full_features_dict['location_multiplier'],# 4
        text_severity_combined,                   # 5
        full_features_dict['upvote_count_normalized'], # 6
        risk_factor                               # 7
    ]
    
    # Return both the formatted vector and the full dictionary
    return np.array(model_features).reshape(1, -1), full_features_dict

def predict_with_trained_model(
    object_detection_result: Dict,
    scene_classification_result: Dict,
    location_context_result: Optional[Dict] = None,
    text_analysis_result: Optional[Dict] = None,
    upvote_count: int = 0,
    model_path: str = "ai_service/models/parent_severity_model.pkl"
) -> Optional[Dict]:
    """
    Use the trained model to predict severity
    
    Returns:
        Dict with severity_score and confidence, or None if model not available
    """
    model = load_trained_model(model_path)
    
    if model is None:
        return None
    
    try:
        # Prepare features
        features, full_features_dict = prepare_features_for_model(
            object_detection_result,
            scene_classification_result,
            location_context_result,
            text_analysis_result,
            upvote_count
        )
        
        # Make prediction (raw score)
        # Adjust based on your model type (classifier, regressor, etc.)
        if hasattr(model, 'predict_proba'):
            # Classification model with probability
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            confidence = float(max(probabilities))
            
            # Map prediction to severity score (0-100)
            # Adjust this based on your model's output
            if isinstance(prediction, (int, np.integer)):
                # If model outputs class (0-4 for Clean/Low/Medium/High/Extreme)
                raw_score = (prediction + 1) * 20  # Map to 20, 40, 60, 80, 100
            else:
                raw_score = float(prediction)
        
        elif hasattr(model, 'predict'):
            # Regression model
            raw_score = float(model.predict(features)[0])
            raw_score = np.clip(raw_score, 0, 100)
            
            # Estimate confidence based on model type
            if hasattr(model, 'score'):
                confidence = 0.8  # Default for regression
            else:
                confidence = 0.75
        
        else:
            print(f"⚠️  Unknown model type: {type(model)}")
            return None
        
        # Apply calibration AFTER model prediction
        severity_score = calibrate_severity_score(raw_score)
        
        return {
            'severity_score': severity_score,
            'raw_score': raw_score,  # Include raw score for debugging
            'confidence': confidence,
            'model_type': type(model).__name__,
            'calibrated': True,
            'input_features': full_features_dict  # Return all 21 features for frontend
        }
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return None

def get_feature_names() -> list:
    """
    Return the list of feature names in order
    Useful for debugging and understanding the model
    """
    return [
        # Object detection (6 features)
        'object_count',
        'coverage_area',
        'density',
        'has_overflow',
        'is_open_dump',
        'bin_detected',
        
        # Scene classification (4 features)
        'dirtiness_score',
        'scene_confidence',
        'dirty_indicators',
        'clean_indicators',
        
        # Location context (5 features)
        'location_multiplier',
        'zone_educational',
        'zone_healthcare',
        'zone_eco',
        'zone_residential',
        
        # Text sentiment (5 features)
        'sentiment_score',
        'text_boost_normalized',
        'urgency_critical',
        'urgency_high',
        'urgency_medium',
        
        # Social signals (1 feature)
        'upvote_count_normalized'
    ]

# Feature count for validation
EXPECTED_FEATURE_COUNT = 21
