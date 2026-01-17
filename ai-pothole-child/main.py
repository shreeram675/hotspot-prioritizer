from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
import io
from PIL import Image
import numpy as np

from model_loader import pothole_models
from osm_utils import analyze_location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pothole-child")

app = FastAPI(title="Pothole Child Models Service", version="1.0")

class LocationInput(BaseModel):
    latitude: float
    longitude: float

class SentimentInput(BaseModel):
    text: str

@app.on_event("startup")
def startup_event():
    """Load all models at startup"""
    pothole_models.load_models()
    logger.info("Pothole child models service ready on port 8001")

@app.post("/analyze_image")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze pothole image using YOLO and Depth models.
    Returns: spread_score, depth_score
    """
    try:
        # Read image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # 1. YOLO Segmentation for spread
        yolo_model = pothole_models.get_yolo()
        results = yolo_model(pil_image)
        
        spread_score = 0.0
        pothole_count = 0
        
        if len(results) > 0 and results[0].masks is not None:
            masks = results[0].masks.data.cpu().numpy()
            pothole_count = len(masks)
            
            # Calculate total pothole area
            total_mask = np.any(masks, axis=0)
            pothole_area = np.sum(total_mask)
            total_area = total_mask.shape[0] * total_mask.shape[1]
            
            area_percentage = (pothole_area / total_area) * 100
            
            # Map to score
            if area_percentage > 5:
                spread_score = 1.0
            elif area_percentage > 2:
                spread_score = 0.7
            elif area_percentage > 0.5:
                spread_score = 0.4
            else:
                spread_score = 0.2
        
        # 2. Depth Estimation
        depth_pipeline = pothole_models.get_depth_pipeline()
        depth_result = depth_pipeline(pil_image)
        depth_map = np.array(depth_result['depth'])
        
        # Calculate relative depth score
        if pothole_count > 0:
            # Use YOLO mask to analyze depth within pothole
            masked_depth = depth_map[total_mask]
            avg_depth = np.mean(masked_depth)
            max_depth = np.max(masked_depth)
            
            # Normalize (higher values = deeper)
            depth_score = min(max_depth / 255.0, 1.0)
        else:
            depth_score = 0.0
        
        return {
            "spread_score": round(spread_score, 3),
            "depth_score": round(depth_score, 3),
            "pothole_count": pothole_count,
            "area_percentage": round(area_percentage, 2) if pothole_count > 0 else 0.0
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
        sentiment_pipeline = pothole_models.get_sentiment_pipeline()
        result = sentiment_pipeline(input_data.text)[0]
        
        # Map NEGATIVE sentiment to urgency
        if result['label'] == 'NEGATIVE':
            emotion_score = result['score']
        else:
            emotion_score = 0.1  # Baseline for positive/neutral
        
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
        "service": "pothole-child-models",
        "port": 8001
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
