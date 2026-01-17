from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
import io
from PIL import Image
import numpy as np

from model_loader import garbage_models
from osm_utils import analyze_location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("garbage-child")

app = FastAPI(title="Garbage Child Models Service", version="1.0")

class LocationInput(BaseModel):
    latitude: float
    longitude: float

class SentimentInput(BaseModel):
    text: str

@app.on_event("startup")
def startup_event():
    """Load all models at startup"""
    garbage_models.load_models()
    logger.info("Garbage child models service ready on port 8002")

@app.post("/analyze_image")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze garbage image using YOLO and waste classifier.
    Returns: volume_score, waste_type_score
    """
    try:
        # Read image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # 1. YOLO Detection for volume estimation
        yolo_model = garbage_models.get_yolo()
        results = yolo_model(pil_image)
        
        volume_score = 0.0
        garbage_count = 0
        
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            garbage_count = len(boxes)
            
            # Calculate total area covered by detected objects
            total_area = 0
            image_area = pil_image.size[0] * pil_image.size[1]
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                box_area = (x2 - x1) * (y2 - y1)
                total_area += box_area
            
            area_percentage = (total_area / image_area) * 100
            
            # Map to volume score
            if area_percentage > 20:
                volume_score = 1.0
            elif area_percentage > 10:
                volume_score = 0.7
            elif area_percentage > 5:
                volume_score = 0.4
            else:
                volume_score = 0.2
        
        # 2. Waste Type Classification (hazardous vs organic)
        classifier = garbage_models.get_classifier()
        
        # Use zero-shot classification to determine waste type
        waste_types = ["hazardous waste", "organic waste", "recyclable waste", "general waste"]
        classification = classifier(pil_image, candidate_labels=waste_types)
        
        # Map to hazard score
        top_label = classification['labels'][0]
        confidence = classification['scores'][0]
        
        if top_label == "hazardous waste":
            waste_type_score = confidence
        elif top_label == "organic waste":
            waste_type_score = 0.3
        else:
            waste_type_score = 0.5
        
        return {
            "volume_score": round(volume_score, 3),
            "waste_type_score": round(waste_type_score, 3),
            "garbage_count": garbage_count,
            "area_percentage": round(area_percentage, 2) if garbage_count > 0 else 0.0,
            "waste_type": top_label
        }
    
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_sentiment")
async def analyze_sentiment(input_data: SentimentInput):
    """
    Analyze text sentiment for urgency.
    Returns: emotion_score (0-1)
    """
    try:
        sentiment_pipeline = garbage_models.get_sentiment_pipeline()
        result = sentiment_pipeline(input_data.text)[0]
        
        if result['label'] == 'NEGATIVE':
            emotion_score = result['score']
        else:
            emotion_score = 0.1
        
        return {
            "emotion_score": round(emotion_score, 3),
            "sentiment": result['label'],
            "confidence": round(result['score'], 3)
        }
    
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_location")
async def analyze_location_endpoint(input_data: LocationInput):
    """
    Analyze location context using OSM.
    Returns: location_score (0-1)
    """
    try:
        result = analyze_location(input_data.latitude, input_data.longitude)
        return result
    
    except Exception as e:
        logger.error(f"Location analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "garbage-child-models",
        "port": 8002
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
