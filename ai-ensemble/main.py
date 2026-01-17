from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
from PIL import Image
import io
import numpy as np

from model_loader import model_loader
from osm_utils import get_location_context

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-ensemble")

app = FastAPI(title="AI Ensemble Severity Analysis")

class AnalysisResult(BaseModel):
    visual_severity_score: float
    urgency_score: float
    location_impact_score: float
    final_priority_score: float
    details: dict

@app.on_event("startup")
def startup_event():
    model_loader.load_models()

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_report(
    description: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    image: UploadFile = File(...)
):
    """
    Performs multi-model analysis on a submitted pothole report.
    """
    logger.info("Received analysis request")
    
    # Read Image Once
    image_bytes = await image.read()
    pil_image = Image.open(io.BytesIO(image_bytes))

    # 1. VISUAL SPREAD ANALYSIS (YOLOv8)
    visual_score = 0.0
    pothole_details = {"count": 0, "max_area_ratio": 0.0}
    
    try:
        model = model_loader.get_pothole_model()
        results = model(pil_image)
        
        for r in results:
            if r.boxes:
                pothole_details["count"] = len(r.boxes)
                img_area = r.orig_shape[0] * r.orig_shape[1]
                
                max_box_area = 0
                for box in r.boxes:
                    w = box.xywh[0][2].item()
                    h = box.xywh[0][3].item()
                    area = w * h
                    if area > max_box_area:
                        max_box_area = area
                
                ratio = max_box_area / img_area
                pothole_details["max_area_ratio"] = ratio
                
                if ratio > 0.05:
                    visual_score = 1.0
                elif ratio > 0.01:
                    visual_score = 0.6
                else:
                    visual_score = 0.3
            else:
                visual_score = 0.0

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")

    # 2. DEPTH ANALYSIS (Depth Anything)
    depth_score = 0.0
    depth_details = {"max_depth_value": 0.0, "is_deep": False}
    try:
        depth_pipe = model_loader.get_depth_pipeline()
        # Returns a dict with 'predicted_depth' (PIL Image) or 'depth' tensor depending on invocation
        # Pipeline "depth-estimation" usually returns {'predicted_depth': tensor, 'depth': PIL Image}
        depth_out = depth_pipe(pil_image)
        
        # approximate relative depth logic:
        # the model outputs relative depth. We need to check if the area *inside* the pothole is significantly
        # "deeper" (further away/darker/lighter depending on map) than the road surface.
        # Simple heuristic: Mean depth intensity of image vs Mean depth intensity of pothole center.
        
        # For this version, we will use a simpler proxy:
        # Just return a placeholder score until we have the tensor manipulation logic perfect.
        # But to be "real", let's assume if it sees high contrast variations it might include depth.
        # Actually, let's trust the model:
        prediction = depth_out["predicted_depth"] # tensor usually
        
        # Normalize simple check provided by pipeline
        # Since 'predicted_depth' is relative, higher usually means further/deeper.
        # We assign a mid-range score for now as a safe default if calculation complex.
        depth_score = 0.5 
        
        # TODO: Refine this to mask the depth map with the YOLO mask for precise depth.
        
    except Exception as e:
        logger.error(f"Depth analysis failed: {e}")

    # 3. SENTIMENT ANALYSIS (DistilBERT)
    urgency_score = 0.0
    sentiment_details = {}
    try:
        nlp = model_loader.get_sentiment_pipeline()
        sentiment_result = nlp(description[:512])[0]
        sentiment_details = sentiment_result
        
        if sentiment_result['label'] == 'NEGATIVE':
            urgency_score = sentiment_result['score']
        else:
            urgency_score = 0.1
            
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")

    # 4. CONTEXT ANALYSIS (OSM)
    location_context = get_location_context(lat, lon)
    location_score = location_context["score"]

    # 5. PARENT MODEL (ENSEMBLE LOGIC)
    # Weights Revised
    W_VISUAL = 0.4  # Spread/Area
    W_DEPTH = 0.3   # Depth
    W_LOCATION = 0.2 # Context
    W_URGENCY = 0.1 # Sentiment
    
    final_score = (
        (W_VISUAL * visual_score) +
        (W_DEPTH * depth_score) +
        (W_LOCATION * location_score) +
        (W_URGENCY * urgency_score)
    )
    
    # Severity Boost for Deep Holes (Simulated for now if depth_score > 0.8)
    if depth_score > 0.8:
        final_score = max(final_score, 0.8)

    final_priority = round(final_score * 100, 2)
    
    return AnalysisResult(
        visual_severity_score=visual_score,
        urgency_score=urgency_score,
        location_impact_score=location_score,
        final_priority_score=final_priority,
        details={
            "pothole": pothole_details,
            "depth": depth_details,
            "sentiment": sentiment_details,
            "location": location_context
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
