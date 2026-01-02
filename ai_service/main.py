from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
import model
import logic
import object_detector
import scene_classifier
import waste_classifier
from severity_scorer import SeverityScorer

app = FastAPI(title="Garbage Detection AI Service")

class DetectionResult(BaseModel):
    is_garbage: bool
    detected_category: str | None
    confidence: float
    garbage_type: str | None
    all_predictions: List[dict]

class ObjectDetectionResult(BaseModel):
    object_count: int
    coverage_area: float
    density: float
    has_overflow: bool
    is_open_dump: bool
    bin_detected: bool
    detections: List[dict]

class SceneClassificationResult(BaseModel):
    dirtiness_score: float
    cleanliness_category: str
    top_predictions: List[dict]
    confidence: float
    dirty_indicators: float
    clean_indicators: float

class SeverityAnalysisResult(BaseModel):
    severity_score: int
    severity_category: str
    confidence: float
    explanation: str
    component_scores: dict
    object_detection: ObjectDetectionResult
    scene_classification: SceneClassificationResult

class BatchSeverityResult(BaseModel):
    results: List[SeverityAnalysisResult]
    summary: dict

@app.on_event("startup")
async def startup_event():
    # Preload models
    print("Loading models...")
    model.get_model()  # MobileNetV2 for legacy detection
    scene_classifier.get_scene_model()  # MobileNetV2 for scene analysis
    object_detector.get_yolo_model()  # YOLOv8n for object detection
    
    # Preload NLP model
    try:
        import text_analyzer
        text_analyzer.get_sentiment_analyzer()  # DistilBERT for sentiment
        print("NLP sentiment analyzer loaded")
    except Exception as e:
        print(f"Warning: Could not preload NLP model: {e}")
    
    print("All models loaded successfully")

@app.post("/detect", response_model=DetectionResult)
async def detect_object(file: UploadFile = File(...)):
    """
    Legacy endpoint for basic garbage detection
    Maintained for backward compatibility
    """
    contents = await file.read()
    
    probs, indices = model.predict_image(contents)
    
    # Check Top-1
    top_class_idx = indices[0]
    top_prob = probs[0]
    
    predicted_category = logic.get_predicted_category(top_class_idx)
    predicted_label = logic.get_label(top_class_idx) if predicted_category else None
    
    # If no category detected, result is False/None
    is_detected = predicted_category is not None

    predictions = []
    for i in range(len(indices)):
        idx = indices[i]
        cat = logic.get_predicted_category(idx)
        predictions.append({
            "class_id": idx,
            "label": logic.get_label(idx) if cat else "Other",
            "confidence": probs[i],
            "category": cat
        })

    return {
        "is_garbage": is_detected,
        "detected_category": predicted_category,
        "garbage_type": predicted_label,
        "confidence": top_prob if is_detected else 0.0,
        "all_predictions": predictions
    }

@app.post("/analyze-severity", response_model=SeverityAnalysisResult)
async def analyze_severity(
    file: UploadFile = File(...),
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    description: Optional[str] = None,
    upvote_count: int = 0
):
    """
    Comprehensive garbage severity analysis using multiple AI models + context
    
    Args:
        file: Image file to analyze
        lat: Optional latitude for location context
        lon: Optional longitude for location context
        description: Optional user description for text sentiment analysis
        upvote_count: Number of upvotes (social validation)
    
    Returns:
        - Object detection results (YOLO)
        - Scene classification results (MobileNetV2)
        - Location context analysis (if coordinates provided)
        - Text sentiment analysis (if description provided)
        - Unified severity score (0-100)
        - Severity category (Clean/Low/Medium/High/Extreme)
        - Confidence and comprehensive explanation
    """
    contents = await file.read()
    
    # Run image analysis models
    obj_detection = object_detector.detect_garbage_objects(contents)
    scene_analysis = scene_classifier.analyze_scene_cleanliness(contents)
    
    # Run location context analysis if coordinates provided
    location_context = None
    if lat is not None and lon is not None:
        try:
            import location_analyzer
            location_context = location_analyzer.analyze_location_context(lat, lon)
        except Exception as e:
            print(f"Location analysis error: {e}")
    
    # Run text sentiment analysis if description provided
    text_analysis = None
    if description:
        try:
            import text_analyzer
            text_analysis = text_analyzer.analyze_text_sentiment(description)
        except Exception as e:
            print(f"Text analysis error: {e}")
    
    # Run waste type classification
    waste_classification = waste_classifier.classify_waste_from_detections(
        obj_detection.get('detections', []),
        description or ''
    )
    
    # Calculate unified severity score with all context
    severity_result = SeverityScorer.calculate_severity(
        object_detection_result=obj_detection,
        scene_classification_result=scene_analysis,
        location_context_result=location_context,
        text_analysis_result=text_analysis,
        upvote_count=upvote_count
    )
    
    # Combine all results
    response = {
        **severity_result,
        "object_detection": obj_detection,
        "scene_classification": scene_analysis
    }
    
    # Add optional context results if available
    if location_context:
        response["location_context"] = location_context
    
    if text_analysis:
        response["text_analysis"] = text_analysis
    
    # Add waste classification
    response["waste_classification"] = waste_classification
    
    return response

@app.post("/analyze-severity-batch", response_model=BatchSeverityResult)
async def analyze_severity_batch(files: List[UploadFile] = File(...)):
    """
    Batch analysis for multiple images
    Useful for city monitoring and hotspot identification
    
    Returns:
    - Individual severity results for each image
    - Summary statistics (average severity, hotspot count, priority level)
    """
    results = []
    
    for file in files:
        contents = await file.read()
        
        # Run analysis for each image
        obj_detection = object_detector.detect_garbage_objects(contents)
        scene_analysis = scene_classifier.analyze_scene_cleanliness(contents)
        
        severity_result = SeverityScorer.calculate_severity(
            object_detection_result=obj_detection,
            scene_classification_result=scene_analysis
        )
        
        results.append({
            **severity_result,
            "object_detection": obj_detection,
            "scene_classification": scene_analysis
        })
    
    # Calculate batch summary
    summary = SeverityScorer.calculate_batch_summary(results)
    
    return {
        "results": results,
        "summary": summary
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models": {
            "legacy_detection": "mobilenet_v2",
            "object_detection": "yolov8n",
            "scene_classification": "mobilenet_v2",
            "text_sentiment": "distilbert",
            "location_analysis": "openstreetmap_api"
        }
    }

