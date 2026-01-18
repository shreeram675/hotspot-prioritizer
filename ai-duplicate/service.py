from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import difflib
import math

app = FastAPI(title="AI Duplicate Detection Service (Lightweight)")

# --------------------------
# Lightweight Logic Models
# --------------------------

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: List[float]

class Candidate(BaseModel):
    id: int
    text: str

class DuplicateCheckRequest(BaseModel):
    new_report_text: str
    candidates: List[Candidate]

class DuplicateMatch(BaseModel):
    id: int
    score: float

class DuplicateCheckResponse(BaseModel):
    matches: List[DuplicateMatch]

class CategoryRequest(BaseModel):
    text: str

class CategoryResponse(BaseModel):
    category: str
    confidence: float
    all_scores: dict

class SeverityRequest(BaseModel):
    text: str

class SeverityResponse(BaseModel):
    severity: str
    confidence: float

class PriorityRequest(BaseModel):
    text: str
    latitude: float
    longitude: float
    upvotes: int = 0

class PriorityResponse(BaseModel):
    priority: str
    confidence: float
    factors: dict

# --------------------------
# Endpoints
# --------------------------

@app.get("/")
def root():
    return {"message": "ai-duplicate service is running (Lightweight Mode)"}

@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    """
    Generate a simple 'hash-like' embedding for MVP compatibility.
    Real vector DBs need real floats, so we simulate a deterministic vector 
    based on character counts/content to ensure non-crashing.
    """
    # Deterministic pseudo-random vector based on content (size 384 to match MiniLM)
    import random
    random.seed(request.text) 
    embedding = [random.random() for _ in range(384)]
    return {"embedding": embedding}

@app.post("/check_duplicates", response_model=DuplicateCheckResponse)
def check_duplicates(request: DuplicateCheckRequest):
    """
    Use Python's built-in SequenceMatcher for text similarity.
    Robust, fast, no deps.
    """
    if not request.candidates:
        return {"matches": []}

    matches = []
    new_text = request.new_report_text.lower()
    
    for candidate in request.candidates:
        cand_text = candidate.text.lower()
        # Calculate similarity ratio (0.0 to 1.0)
        score = difflib.SequenceMatcher(None, new_text, cand_text).ratio()
        
        if score > 0.6: # Threshold
            matches.append(DuplicateMatch(id=candidate.id, score=score))
            
    matches.sort(key=lambda x: x.score, reverse=True)
    return {"matches": matches}

@app.post("/predict_category", response_model=CategoryResponse)
def predict_category(request: CategoryRequest):
    """
    Keyword-based intent classification.
    """
    text = request.text.lower()
    
    # Keyword mapping
    categories = {
        "pothole": ["pothole", "road", "tarmac", "asphalt", "hole", "street"],
        "garbage": ["garbage", "trash", "rubbish", "waste", "bin", "dump", "dirty", "smell"],
        "street_light": ["light", "lamp", "dark", "pole", "bulb"],
        "flooding": ["flood", "water", "rain", "drain", "blocked"],
        "graffiti": ["graffiti", "paint", "wall", "vandalism"],
        "noise_complaint": ["noise", "loud", "music", "sound"],
    }
    
    best_cat = "other"
    best_score = 0.0
    all_scores = {}
    
    for cat, keywords in categories.items():
        score = 0.0
        for k in keywords:
            if k in text:
                score += 0.3
        
        # Normalize roughly to 0-1
        score = min(score, 1.0)
        if score == 0: score = 0.05 # small epilson
        
        all_scores[cat] = score
        if score > best_score:
            best_score = score
            best_cat = cat
            
    return {
        "category": best_cat,
        "confidence": best_score,
        "all_scores": all_scores
    }

@app.post("/predict_severity", response_model=SeverityResponse)
def predict_severity(request: SeverityRequest):
    text = request.text.lower()
    
    severity = "medium"
    confidence = 0.5
    
    if any(w in text for w in ["danger", "accident", "huge", "critical", "death", "severe"]):
        severity = "critical"
        confidence = 0.9
    elif any(w in text for w in ["urgent", "bad", "deep", "large", "fast"]):
        severity = "high"
        confidence = 0.8
    elif any(w in text for w in ["low", "minor", "small", "fix"]):
        severity = "low"
        confidence = 0.7
        
    return {"severity": severity, "confidence": confidence}

@app.post("/predict_priority", response_model=PriorityResponse)
def predict_priority(request: PriorityRequest):
    # Reuse the logic which was already largely keyword based
    priority_score = 0.0
    factors = {}
    
    text_lower = request.text.lower()
    
    # Loc
    if any(w in text_lower for w in ["school", "college", "hospital", "clinic"]):
        priority_score += 0.4
        factors["location_sensitive"] = "school/hospital"
    
    # Upvotes
    uv_score = min(request.upvotes / 20.0, 1.0) * 0.3
    priority_score += uv_score
    factors["upvotes"] = request.upvotes
    
    # Urgency
    if "urgent" in text_lower or "critical" in text_lower:
        priority_score += 0.3
        factors["urgency"] = "high"
        
    # Determine level
    if priority_score >= 0.7: level = "critical"
    elif priority_score >= 0.5: level = "high"
    elif priority_score >= 0.3: level = "medium"
    else: level = "low"
    
    return {
        "priority": level,
        "confidence": priority_score,
        "factors": factors
    }
