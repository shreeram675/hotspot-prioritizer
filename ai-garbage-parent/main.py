from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import logging
import os
import torch

from model_loader import garbage_model_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("garbage-parent")

app = FastAPI(title="Garbage Severity Prediction Service")

class SeverityInput(BaseModel):
    # The 7 Hybrid Inputs
    object_count: float = Field(..., description="1. Count from YOLO")
    coverage_area: float = Field(..., description="2. Area % from YOLO")
    dirtiness_score: float = Field(..., description="3. CNN Score")
    location_multiplier: float = Field(..., description="4. Location Logic")
    text_severity: float = Field(..., description="5. NLP Score")
    social_score: float = Field(..., description="6. Upvote Norm")
    risk_factor: float = Field(..., description="7. Keyword Flag")

class SeverityOutput(BaseModel):
    severity_score: float
    severity_level: str

@app.on_event("startup")
def startup_event():
    """Load model"""
    # Note: User file is parent_severity_model.pkl (or .py per confusion, but assuming pickle logic)
    model_path = os.getenv(
        "GARBAGE_MODEL_PATH",
        r"models/parent_severity_model.pkl" 
    )
    garbage_model_loader.load_model(model_path)
    logger.info("Garbage severity prediction service ready (Hybrid Mode)")

@app.post("/predict", response_model=SeverityOutput)
def predict(input_data: SeverityInput):
    """Predict severity using Hybrid Parent Model"""
    try:
        model, device = garbage_model_loader.get_model()
        
        # Construct 7-dim vector
        features = [
            input_data.object_count,
            input_data.coverage_area,
            input_data.dirtiness_score,
            input_data.location_multiplier,
            input_data.text_severity,
            input_data.social_score,
            input_data.risk_factor
        ]
        
        severity = 0.0
        
        if model:
            # Check if model is sklearn/pickle (no tensor needed) or PyTorch
            try:
                # Try sklearn style first (predict takes numpy 2d array)
                import numpy as np
                input_array = np.array([features])
                prediction = model.predict(input_array)
                severity = float(prediction[0])
            except:
                # Fallback to PyTorch style
                input_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(device)
                with torch.no_grad():
                    output = model(input_tensor)
                    severity = output.item()
        
        else:
            # Robust Fallback Formula (AGRESSIVE TUNING)
            # User Feedback: "scale it a bit larger" for huge garbage
            s = ( 
                (input_data.coverage_area * 100 * 0.45) +       # Boosted from 0.3
                (input_data.dirtiness_score * 100 * 0.35) +     # Boosted from 0.2
                (input_data.text_severity * 100 * 0.1) + 
                (input_data.location_multiplier * 100 * 0.2) +
                (input_data.social_score * 100 * 0.1) +
                (input_data.risk_factor * 100 * 0.2)            # Boosted from 0.1
            )
            # This sum can exceed 100, so we clamp it at the end
            severity = s

        # --- POST-PREDICTION BOOST ---
        # "Make the score a bit larger scale it is showing low score for a huge garbage"
        if input_data.coverage_area > 0.4:
            # If >40% of image is trash, boost severity by 1.25x
            severity *= 1.25
        
        # Ensure Hazard Level impact is critical
        if input_data.risk_factor > 0.8:
             severity = max(severity, 85.0) # Immediate Critical if toxic/medical
        
        if input_data.risk_factor > 0.8:
             severity = max(severity, 85.0) # Immediate Critical if toxic/medical
        
        # --- CLEAN OVERRIDE ---
        # If visually clean (low coverage & low dirtiness), force low score
        if input_data.coverage_area < 0.1 and input_data.dirtiness_score < 0.15:
            severity *= 0.1
            
        severity_score = max(0.0, min(100.0, severity))
        
        if severity_score >= 80:
            severity_level = "critical"
        elif severity_score >= 60:
            severity_level = "high"
        elif severity_score >= 40:
            severity_level = "medium"
        else:
            severity_level = "low"
        
        return SeverityOutput(
            severity_score=round(severity_score, 2),
            severity_level=severity_level
        )
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "garbage-parent-model",
        "port": 8004,
        "model_loaded": garbage_model_loader._model is not None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
