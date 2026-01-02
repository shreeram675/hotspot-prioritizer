"""
Text Sentiment Analyzer
Analyzes user descriptions for urgency, emotion, and severity indicators using NLP
"""
from transformers import pipeline
from typing import Dict, List
import re

# Singleton sentiment analyzer
_sentiment_analyzer = None

# Urgency keywords with severity weights
URGENCY_KEYWORDS = {
    'critical': 30,
    'emergency': 30,
    'urgent': 25,
    'immediate': 25,
    'dangerous': 25,
    'hazardous': 25,
    'overflowing': 20,
    'overflow': 20,
    'severe': 20,
    'terrible': 18,
    'awful': 18,
    'disgusting': 15,
    'smelly': 15,
    'stinking': 15,
    'health hazard': 25,
    'health risk': 25,
    'blocking': 15,
    'blocked': 15,
    'piling up': 15,
    'everywhere': 12,
    'spreading': 12,
}

def get_sentiment_analyzer():
    """Load and cache sentiment analysis model"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        print("Loading DistilBERT sentiment analyzer...")
        # Using distilbert-base-uncased-finetuned-sst-2-english for sentiment
        _sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1  # CPU
        )
        print("Sentiment analyzer loaded successfully")
    return _sentiment_analyzer

def extract_urgency_keywords(text: str) -> List[Dict]:
    """
    Extract urgency keywords from text
    
    Returns:
        List of dicts with keyword and weight
    """
    text_lower = text.lower()
    found_keywords = []
    
    for keyword, weight in URGENCY_KEYWORDS.items():
        if keyword in text_lower:
            found_keywords.append({
                'keyword': keyword,
                'weight': weight
            })
    
    # Sort by weight descending
    found_keywords.sort(key=lambda x: x['weight'], reverse=True)
    
    return found_keywords

def detect_emotion_category(sentiment_result: Dict) -> str:
    """
    Categorize emotion based on sentiment analysis
    
    Returns:
        'angry', 'concerned', 'neutral', or 'positive'
    """
    label = sentiment_result['label']
    score = sentiment_result['score']
    
    if label == 'NEGATIVE':
        if score > 0.9:
            return 'angry'
        elif score > 0.7:
            return 'concerned'
        else:
            return 'neutral'
    else:  # POSITIVE
        if score > 0.8:
            return 'positive'
        else:
            return 'neutral'

def calculate_text_severity_boost(urgency_keywords: List[Dict], sentiment_score: float) -> int:
    """
    Calculate severity boost from text analysis
    
    Args:
        urgency_keywords: List of found urgency keywords
        sentiment_score: Sentiment score (0-1, where 1 is most negative/urgent)
    
    Returns:
        Severity boost points (0-30)
    """
    if not urgency_keywords:
        # No urgency keywords, use sentiment only
        return int(sentiment_score * 10)  # Max 10 points from sentiment
    
    # Use highest weight keyword
    max_keyword_weight = urgency_keywords[0]['weight']
    
    # Combine keyword weight with sentiment
    # Keyword contributes 70%, sentiment contributes 30%
    boost = (max_keyword_weight * 0.7) + (sentiment_score * 10 * 0.3)
    
    return min(int(boost), 30)  # Cap at 30 points

def analyze_text_sentiment(description: str) -> Dict:
    """
    Analyze text description for sentiment, urgency, and emotion
    
    Args:
        description: User-provided report description
    
    Returns:
        Dict containing:
        - sentiment_score: 0-1 (higher = more negative/urgent)
        - emotion: angry/concerned/neutral/positive
        - urgency_level: critical/high/medium/low
        - keywords: List of urgency keywords found
        - severity_boost: Points to add to severity (0-30)
    """
    if not description or len(description.strip()) < 5:
        # Too short or empty
        return {
            'sentiment_score': 0.0,
            'emotion': 'neutral',
            'urgency_level': 'low',
            'keywords': [],
            'severity_boost': 0
        }
    
    try:
        # Run sentiment analysis
        analyzer = get_sentiment_analyzer()
        
        # Truncate to 512 tokens if needed
        text = description[:500]
        
        result = analyzer(text)[0]
        
        # Convert to urgency score (0-1, where 1 is most urgent)
        # NEGATIVE sentiment with high confidence = high urgency
        if result['label'] == 'NEGATIVE':
            sentiment_score = result['score']
        else:
            sentiment_score = 1 - result['score']  # Invert positive sentiment
        
        # Extract urgency keywords
        keywords = extract_urgency_keywords(description)
        
        # Detect emotion
        emotion = detect_emotion_category(result)
        
        # Calculate severity boost
        severity_boost = calculate_text_severity_boost(keywords, sentiment_score)
        
        # Determine urgency level
        if severity_boost >= 25 or (keywords and keywords[0]['weight'] >= 25):
            urgency_level = 'critical'
        elif severity_boost >= 18 or sentiment_score > 0.8:
            urgency_level = 'high'
        elif severity_boost >= 10 or sentiment_score > 0.5:
            urgency_level = 'medium'
        else:
            urgency_level = 'low'
        
        return {
            'sentiment_score': round(sentiment_score, 3),
            'emotion': emotion,
            'urgency_level': urgency_level,
            'keywords': [kw['keyword'] for kw in keywords[:5]],  # Top 5 keywords
            'severity_boost': severity_boost
        }
        
    except Exception as e:
        print(f"Error in text sentiment analysis: {e}")
        # Return neutral analysis on error
        return {
            'sentiment_score': 0.0,
            'emotion': 'neutral',
            'urgency_level': 'low',
            'keywords': [],
            'severity_boost': 0
        }
