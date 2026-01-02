"""
Hybrid Severity Scorer - Combines Trained Model with Rule-Based Approach
Uses trained .pkl model when available, falls back to rule-based scoring
"""
from typing import Dict, Optional
from severity_scorer import SeverityScorer
import trained_model_loader

class HybridSeverityScorer:
    """
    Hybrid approach that uses trained model when available,
    falls back to rule-based scoring otherwise
    """
    
    @staticmethod
    def calculate_severity(
        object_detection_result: Dict,
        scene_classification_result: Dict,
        location_context_result: Optional[Dict] = None,
        text_analysis_result: Optional[Dict] = None,
        upvote_count: int = 0,
        use_trained_model: bool = True,
        model_path: str = "ai_service/models/parent_severity_model.pkl"
    ) -> Dict:
        """
        Calculate severity using hybrid approach
        
        Args:
            object_detection_result: YOLO output
            scene_classification_result: Scene classifier output
            location_context_result: Location analyzer output
            text_analysis_result: Text sentiment output
            upvote_count: Social validation
            use_trained_model: Whether to try using trained model first
            model_path: Path to .pkl file
            
        Returns:
            Dict with severity score, category, and metadata
        """
        
        trained_prediction = None
        
        # Try trained model first if enabled
        if use_trained_model:
            trained_prediction = trained_model_loader.predict_with_trained_model(
                object_detection_result,
                scene_classification_result,
                location_context_result,
                text_analysis_result,
                upvote_count,
                model_path
            )
        
        # Get rule-based prediction as well (for comparison or fallback)
        rule_based_result = SeverityScorer.calculate_severity(
            object_detection_result,
            scene_classification_result,
            location_context_result,
            text_analysis_result,
            upvote_count
        )
        
        # Decide which prediction to use
        if trained_prediction is not None:
            # Use trained model prediction
            severity_score = trained_prediction['severity_score']
            confidence = trained_prediction['confidence']
            
            # Map score to category
            severity_category = SeverityScorer._get_category(severity_score)
            
            # Generate explanation (use rule-based explanation for now)
            explanation = rule_based_result['explanation']
            
            # Add note about trained model with calibration info
            if trained_prediction.get('calibrated'):
                raw = trained_prediction.get('raw_score', severity_score)
                explanation += f" [Predicted by trained {trained_prediction['model_type']} model: raw={raw:.1f}, calibrated={severity_score}]"
            
            return {
                'severity_score': severity_score,
                'severity_category': severity_category,
                'confidence': confidence,
                'explanation': explanation,
                'component_scores': rule_based_result['component_scores'],
                'location_multiplier': rule_based_result.get('location_multiplier', 1.0),
                'zone_type': rule_based_result.get('zone_type', 'commercial'),
                'prediction_method': 'trained_model',
                'model_type': trained_prediction['model_type'],
                'raw_score': trained_prediction.get('raw_score'),
                'calibrated': trained_prediction.get('calibrated', False),
                'rule_based_score': rule_based_result['severity_score'],  # For comparison
                'model_input_features': trained_prediction.get('input_features', {}) # Full 21 features
            }
        else:
            # Fall back to rule-based
            rule_based_result['prediction_method'] = 'rule_based'
            return rule_based_result
    
    @staticmethod
    def get_model_info(model_path: str = "ai_service/models/parent_severity_model.pkl") -> Dict:
        """Get information about the loaded model"""
        model = trained_model_loader.load_trained_model(model_path)
        
        if model is None:
            return {
                'loaded': False,
                'path': model_path,
                'message': 'Model not found or failed to load'
            }
        
        return {
            'loaded': True,
            'path': model_path,
            'model_type': type(model).__name__,
            'feature_count': trained_model_loader.EXPECTED_FEATURE_COUNT,
            'features': trained_model_loader.get_feature_names()
        }
