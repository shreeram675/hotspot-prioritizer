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
    Analyze garbage image using HF API (fallback logic for now).
    Returns: volume_score, waste_type_score
    """
    try:
        # Read image
        image_bytes = await image.read()
        
        # 1. Volume Score (Simulated based on inputs for demo)
        import random
        volume_score = round(random.uniform(0.3, 0.9), 2)
        garbage_count = 1
        area_percentage = volume_score * 20.0
        
        # 2. Waste Type Score (Simulated)
        waste_type = "general waste"
        waste_type_score = 0.5
        
        return {
            "volume_score": volume_score,
            "waste_type_score": waste_type_score,
            "garbage_count": garbage_count,
            "area_percentage": area_percentage,
            "waste_type": waste_type
        }
    
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return {
            "volume_score": 0.5,
            "waste_type_score": 0.5,
            "garbage_count": 1,
            "area_percentage": 10.0,
            "waste_type": "unknown"
        }

@app.post("/analyze_sentiment")
    try:
        # Check for critical keywords
        text_lower = input_data.text.lower()
        critical_keywords = ['hazardous', 'toxic', 'chemical', 'medical', 'overflowing', 'smell', 'rat', 'disease', 'urgent']
        
        keyword_boost = 0.0
        found_keywords = []
        for word in critical_keywords:
            if word in text_lower:
                keyword_boost = 0.8
                found_keywords.append(word)

        api_url = garbage_models.get_sentiment_pipeline()
        payload = {"inputs": input_data.text}
        
        response_json = garbage_models.query_api(api_url, payload)
        
        if isinstance(response_json, dict) and "error" in response_json:
             logger.warning(f"API Error: {response_json}")
             emotion_score = keyword_boost if keyword_boost > 0 else 0.5
             label = "UNKNOWN"
             confidence = 0.0
        else:
            if isinstance(response_json, list) and len(response_json) > 0:
                if isinstance(response_json[0], list):
                    top_result = response_json[0][0]
                else:
                    top_result = response_json[0]
                
                label = top_result.get('label', 'NEUTRAL')
                score = top_result.get('score', 0.0)
                
                if label == 'NEGATIVE':
                    emotion_score = score
                else:
                    emotion_score = 0.1
                
                if keyword_boost > 0:
                    emotion_score = max(emotion_score, keyword_boost)
                    
                confidence = score
            else:
                 emotion_score = keyword_boost if keyword_boost > 0 else 0.5
                 label = "UNKNOWN"
                 confidence = 0.0
        
        return {
            "emotion_score": round(emotion_score, 3),
            "sentiment": label,
            "confidence": round(confidence, 3),
            "keywords": found_keywords
        }
    
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return {
            "emotion_score": 0.5,
            "sentiment": "ERROR",
            "confidence": 0.0
        }

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
