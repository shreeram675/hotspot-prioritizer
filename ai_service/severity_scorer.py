"""
Unified Severity Scoring Engine - Enhanced with Context Awareness
Aggregates outputs from multiple AI models + location context + text sentiment
"""
from typing import Dict, Optional
import math

class SeverityScorer:
    """
    Enhanced meta-scoring engine that combines:
    - Image analysis (YOLO + Scene classifier)
    - Location context (proximity to sensitive areas)
    - Text sentiment (NLP analysis of description)
    - Social signals (upvote count)
    - Risk factors (overflow, open dump)
    """
    
    # Enhanced weight distribution for multi-attribute fusion
    WEIGHTS = {
        'image_analysis': 0.40,     # YOLO + Scene classification
        'location_context': 0.25,   # Proximity to schools/hospitals/eco-zones
        'text_sentiment': 0.20,     # NLP urgency/emotion analysis
        'social_signals': 0.10,     # Upvote count
        'risk_factors': 0.05        # Overflow, open dump detection
    }
    
    # Image analysis sub-weights (within 40%)
    IMAGE_SUB_WEIGHTS = {
        'coverage_area': 0.375,     # 15% of total (40% * 0.375)
        'scene_dirtiness': 0.375,   # 15% of total
        'object_count': 0.25        # 10% of total
    }
    
    # Severity category thresholds
    SEVERITY_CATEGORIES = [
        (0, 20, 'Clean'),
        (21, 40, 'Low'),
        (41, 60, 'Medium'),
        (61, 80, 'High'),
        (81, 100, 'Extreme')
    ]
    
    @staticmethod
    def calculate_severity(
        object_detection_result: Dict,
        scene_classification_result: Dict,
        location_context_result: Optional[Dict] = None,
        text_analysis_result: Optional[Dict] = None,
        upvote_count: int = 0
    ) -> Dict:
        """
        Calculate unified severity score from all available inputs
        
        Args:
            object_detection_result: Output from YOLO object detector
            scene_classification_result: Output from scene classifier
            location_context_result: Optional location context analysis
            text_analysis_result: Optional NLP text sentiment analysis
            upvote_count: Number of upvotes (social validation)
            
        Returns:
            Dict containing comprehensive severity assessment
        """
        
        # Extract metrics from object detection
        object_count = object_detection_result.get('object_count', 0)
        coverage_area = object_detection_result.get('coverage_area', 0.0)
        has_overflow = object_detection_result.get('has_overflow', False)
        is_open_dump = object_detection_result.get('is_open_dump', False)
        
        # Extract metrics from scene classification
        dirtiness_score = scene_classification_result.get('dirtiness_score', 0.0)
        scene_confidence = scene_classification_result.get('confidence', 0.5)
        
        # Extract location context
        location_multiplier = 1.0
        zone_type = 'commercial'
        if location_context_result:
            location_multiplier = location_context_result.get('priority_multiplier', 1.0)
            zone_type = location_context_result.get('zone_type', 'commercial')
        
        # Extract text sentiment and risk
        text_boost = 0
        urgency_level = 'low'
        risk_class = 'none'
        nlp_risk_score = 0.0
        
        if text_analysis_result:
            text_boost = text_analysis_result.get('severity_boost', 0)
            urgency_level = text_analysis_result.get('urgency_level', 'low')
            risk_class = text_analysis_result.get('risk_class', 'none')
            nlp_risk_score = text_analysis_result.get('risk_score', 0.0)
        
        # === COMPONENT SCORE CALCULATIONS ===
        
        # 1. Image Analysis Score (0-100)
        # Coverage area sub-score
        coverage_score = min(coverage_area * 200, 100)
        
        # Scene dirtiness sub-score
        scene_score = dirtiness_score * 100
        
        # Object count sub-score (logarithmic scaling)
        if object_count == 0:
            count_score = 0
        else:
            count_score = min(20 + (math.log(object_count) / math.log(50)) * 80, 100)
        
        # Weighted image analysis score
        image_score = (
            coverage_score * SeverityScorer.IMAGE_SUB_WEIGHTS['coverage_area'] +
            scene_score * SeverityScorer.IMAGE_SUB_WEIGHTS['scene_dirtiness'] +
            count_score * SeverityScorer.IMAGE_SUB_WEIGHTS['object_count']
        )
        
        # 2. Location Context Score (0-100)
        # Based on priority multiplier (0.9-1.5 -> 0-100)
        # 1.0 = 50 (baseline), 1.5 = 100 (highest), 0.9 = 0 (lowest)
        location_score = ((location_multiplier - 0.9) / 0.6) * 100
        location_score = max(0, min(location_score, 100))
        
        # 3. Text Sentiment Score (0-100)
        # Direct boost from text analysis (0-30) scaled to 0-100
        text_score = (text_boost / 30) * 100
        
        # 4. Social Signals Score (0-100)
        # Logarithmic scaling: 0 votes=0, 5 votes=50, 20 votes=80, 100+=100
        if upvote_count == 0:
            social_score = 0
        else:
            social_score = min((math.log(upvote_count + 1) / math.log(100)) * 100, 100)
        
        # 5. Risk Factors Score (0-100)
        # 5. Risk Factors Score (0-100)
        # Combine physical risk (overflow/dump) with NLP risk
        risk_score = 0
        # Physical risks
        if has_overflow: risk_score += 40
        if is_open_dump: risk_score += 40
        
        # NLP detected risks
        if risk_class != 'none' and nlp_risk_score > 0.6:
            risk_score += 30  # Add 30 points for confirmed NLP risk
            if risk_class in ['fire hazard', 'toxic chemical', 'medical waste']:
                risk_score += 20  # Additional boost for dangerous risks
        
        risk_score = min(risk_score, 100)
        
        # === WEIGHTED FUSION ===
        base_severity = (
            image_score * SeverityScorer.WEIGHTS['image_analysis'] +
            location_score * SeverityScorer.WEIGHTS['location_context'] +
            text_score * SeverityScorer.WEIGHTS['text_sentiment'] +
            social_score * SeverityScorer.WEIGHTS['social_signals'] +
            risk_score * SeverityScorer.WEIGHTS['risk_factors']
        )
        
        # === APPLY LOCATION MULTIPLIER ===
        # Location multiplier amplifies the final score
        severity_score = base_severity * location_multiplier
        
        # === APPLY TEXT URGENCY BOOST ===
        # Add direct boost for critical/emergency keywords
        if urgency_level == 'critical':
            severity_score += 15
        elif urgency_level == 'high':
            severity_score += 10
        
        # === RISK AMPLIFICATION ===
        # Additional boost for extreme conditions
        if is_open_dump and location_multiplier > 1.2:
            severity_score *= 1.1  # 10% boost for open dump near sensitive area
        
        # Cap at 100
        severity_score = min(round(severity_score), 100)
        
        # Map to category
        severity_category = SeverityScorer._get_category(severity_score)
        
        # Calculate overall confidence
        detection_confidence = 0.8 if object_count > 0 else 0.4
        text_confidence = 0.9 if text_analysis_result else 0.5
        location_confidence = 0.9 if location_context_result else 0.5
        
        overall_confidence = (
            scene_confidence * 0.3 +
            detection_confidence * 0.3 +
            text_confidence * 0.2 +
            location_confidence * 0.2
        )
        
        # Generate comprehensive explanation
        explanation = SeverityScorer._generate_explanation(
            severity_score,
            severity_category,
            object_count,
            coverage_area,
            dirtiness_score,
            location_context_result,
            text_analysis_result,
            upvote_count,
            has_overflow,
            is_open_dump,
            risk_class
        )
        
        return {
            'severity_score': severity_score,
            'severity_category': severity_category,
            'confidence': round(overall_confidence, 3),
            'explanation': explanation,
            'component_scores': {
                'image_analysis_score': round(image_score, 1),
                'location_context_score': round(location_score, 1),
                'text_sentiment_score': round(text_score, 1),
                'social_signals_score': round(social_score, 1),
                'risk_factors_score': round(risk_score, 1)
            },
            'location_multiplier': location_multiplier,
            'zone_type': zone_type
        }
    
    @staticmethod
    def _get_category(score: int) -> str:
        """Map severity score to category"""
        for min_score, max_score, category in SeverityScorer.SEVERITY_CATEGORIES:
            if min_score <= score <= max_score:
                return category
        return 'Unknown'
    
    @staticmethod
    def _generate_explanation(
        score: int,
        category: str,
        object_count: int,
        coverage: float,
        dirtiness: float,
        location_context: Optional[Dict],
        text_analysis: Optional[Dict],
        upvotes: int,
        overflow: bool,
        open_dump: bool,
        risk_class: str = 'none'
    ) -> str:
        """Generate comprehensive human-readable explanation"""
        
        parts = [f"Severity: {category} ({score}/100)."]
        
        # Critical situation flag
        if score >= 80:
            parts.append("⚠️ CRITICAL SITUATION DETECTED.")
        
        # Object count
        if object_count == 0:
            parts.append("No garbage objects detected.")
        elif object_count <= 3:
            parts.append(f"Minimal garbage detected ({object_count} items).")
        elif object_count <= 10:
            parts.append(f"Moderate amount of garbage detected ({object_count} items).")
        else:
            parts.append(f"Significant garbage accumulation ({object_count} items).")
        
        # Coverage
        coverage_pct = round(coverage * 100, 1)
        if coverage_pct > 30:
            parts.append(f"Garbage covers {coverage_pct}% of the visible area.")
        elif coverage_pct > 10:
            parts.append(f"Moderate spread ({coverage_pct}% coverage).")
        
        # Location context
        if location_context and location_context.get('highest_priority_location'):
            loc = location_context['highest_priority_location']
            parts.append(
                f"Located near {loc['name']} ({loc['type']}, {loc['distance_m']}m away)."
            )
            
            if location_context.get('priority_multiplier', 1.0) > 1.2:
                parts.append("HIGH PRIORITY due to sensitive location proximity.")
        
        # Text sentiment
        if text_analysis:
            urgency = text_analysis.get('urgency_level')
            keywords = text_analysis.get('keywords', [])
            
            if urgency in ['critical', 'high']:
                parts.append(f"User description indicates {urgency} urgency.")
            
            if keywords:
                parts.append(f"Keywords: {', '.join(keywords[:3])}.")
        
        # Social validation
        if upvotes > 10:
            parts.append(f"Community validated ({upvotes} upvotes).")
        elif upvotes > 5:
            parts.append(f"Multiple reports ({upvotes} upvotes).")
        
        # Risk factors
        if open_dump:
            parts.append("⚠️ OPEN DUMP DETECTED - Requires immediate attention.")
        
        if risk_class != 'none' and risk_class != 'general waste':
            parts.append(f"⚠️ Risk Detected: {risk_class.upper()}.")
        elif overflow:
            parts.append("⚠️ Potential overflow or heavy accumulation detected.")
        
        # Action recommendation
        if score >= 80:
            parts.append("IMMEDIATE ACTION REQUIRED.")
        elif score >= 60:
            parts.append("Prompt action recommended.")
        
        return " ".join(parts)
    
    @staticmethod
    def calculate_batch_summary(severity_results: list) -> Dict:
        """Calculate summary statistics for multiple images (city monitoring)"""
        if not severity_results:
            return {
                'average_severity': 0,
                'max_severity': 0,
                'hotspot_count': 0,
                'priority_level': 'None'
            }
        
        scores = [r['severity_score'] for r in severity_results]
        categories = [r['severity_category'] for r in severity_results]
        
        avg_severity = round(sum(scores) / len(scores), 1)
        max_severity = max(scores)
        
        # Count high-priority hotspots
        hotspot_count = sum(1 for cat in categories if cat in ['High', 'Extreme'])
        
        # Determine overall priority
        if max_severity >= 80 or hotspot_count >= 3:
            priority = 'Critical'
        elif max_severity >= 60 or hotspot_count >= 2:
            priority = 'High'
        elif avg_severity >= 40:
            priority = 'Medium'
        else:
            priority = 'Low'
        
        return {
            'average_severity': avg_severity,
            'max_severity': max_severity,
            'hotspot_count': hotspot_count,
            'priority_level': priority,
            'total_analyzed': len(severity_results)
        }
