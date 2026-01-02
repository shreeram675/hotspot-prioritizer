"""
Scene-Level Classification Module for Garbage Analysis
Uses MobileNetV2 pretrained on ImageNet to assess overall scene cleanliness
"""
import torch
from torchvision import models, transforms
from PIL import Image
import io
from typing import Dict

# Singleton model instance
_scene_model = None

# ImageNet classes that indicate dirty/cluttered environments
DIRTY_SCENE_CLASSES = {
    # Debris and waste-related
    412: 'ashcan, trash can, garbage can, wastebin, ash bin, ash-bin, ashbin, dustbin, trash barrel, trash bin',
    # Cluttered/messy environments
    516: 'carton',
    673: 'mousetrap',
    696: 'packet',
    723: 'plastic bag',
    898: 'water bottle',
    906: 'wine bottle',
    # Outdoor deteriorated scenes
    637: 'manhole cover',
    # Industrial/construction (often messy)
    536: 'crane',
    569: 'forklift',
}

# Clean environment indicators
CLEAN_SCENE_CLASSES = {
    # Well-maintained outdoor spaces
    449: 'ballplayer, baseball player',
    504: 'carousel, carrousel, merry-go-round, roundabout, whirligig',
    513: 'cornet, horn, trumpet, trump',
    # Indoor clean spaces
    762: 'restaurant, eating house, eating place, eatery',
    # Parks and gardens
    566: 'fountain',
    859: 'totem pole',
}

def get_scene_model():
    """Load and cache MobileNetV2 model for scene classification"""
    global _scene_model
    if _scene_model is None:
        print("Loading MobileNetV2 for scene classification...")
        weights = models.MobileNet_V2_Weights.DEFAULT
        _scene_model = models.mobilenet_v2(weights=weights)
        _scene_model.eval()
        print("MobileNetV2 scene model loaded successfully")
    return _scene_model

def get_scene_transforms():
    """Standard ImageNet transforms"""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

def analyze_scene_cleanliness(image_bytes: bytes) -> Dict:
    """
    Analyze overall scene cleanliness using ImageNet-pretrained model
    
    Returns:
        Dict containing:
        - dirtiness_score: Probability score 0-1 (higher = dirtier)
        - cleanliness_category: Clean / Moderately Dirty / Dirty
        - top_predictions: Top 5 scene predictions
        - confidence: Overall confidence in the assessment
    """
    model = get_scene_model()
    transform = get_scene_transforms()
    
    # Load and transform image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)
    
    # Run inference
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
    
    # Get top 10 predictions for analysis
    top10_prob, top10_idx = torch.topk(probabilities, 10)
    
    # Calculate dirtiness score based on detected classes
    dirty_score = 0.0
    clean_score = 0.0
    
    for prob, idx in zip(top10_prob.tolist(), top10_idx.tolist()):
        if idx in DIRTY_SCENE_CLASSES:
            dirty_score += prob
        if idx in CLEAN_SCENE_CLASSES:
            clean_score += prob
    
    # Normalize and combine scores
    # Base dirtiness on presence of dirty indicators and absence of clean indicators
    dirtiness_score = dirty_score
    
    # If no specific dirty/clean classes detected, use heuristic based on top prediction confidence
    if dirty_score == 0 and clean_score == 0:
        # Low confidence in top prediction might indicate cluttered/unclear scene
        top_confidence = top10_prob[0].item()
        if top_confidence < 0.1:
            dirtiness_score = 0.6  # Unclear scene, assume moderately dirty
        else:
            dirtiness_score = 0.3  # Clear scene, assume relatively clean
    elif clean_score > dirty_score:
        # Reduce dirtiness if clean indicators are stronger
        dirtiness_score = max(0, dirtiness_score - clean_score * 0.5)
    
    # Ensure score is in valid range
    dirtiness_score = min(max(dirtiness_score, 0.0), 1.0)
    
    # Categorize cleanliness
    if dirtiness_score < 0.3:
        category = "Clean"
    elif dirtiness_score < 0.6:
        category = "Moderately Dirty"
    else:
        category = "Dirty"
    
    # Get top 5 predictions for context
    top5_predictions = []
    for i in range(min(5, len(top10_idx))):
        top5_predictions.append({
            'class_id': top10_idx[i].item(),
            'probability': top10_prob[i].item()
        })
    
    # Calculate confidence based on how decisive the scores are
    confidence = abs(dirty_score - clean_score) if (dirty_score + clean_score) > 0 else top10_prob[0].item()
    confidence = min(confidence, 1.0)
    
    return {
        'dirtiness_score': round(dirtiness_score, 3),
        'cleanliness_category': category,
        'top_predictions': top5_predictions,
        'confidence': round(confidence, 3),
        'dirty_indicators': round(dirty_score, 3),
        'clean_indicators': round(clean_score, 3)
    }
