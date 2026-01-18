import httpx
import logging
from typing import Dict, Optional

logger = logging.getLogger("backend")

import os

# AI Service URLs
POTHOLE_CHILD_URL = os.getenv("AI_POTHOLE_CHILD_URL", "http://ai-pothole-child:8001")
POTHOLE_PARENT_URL = os.getenv("AI_POTHOLE_PARENT_URL", "http://ai-pothole-parent:8003")
GARBAGE_CHILD_URL = os.getenv("AI_GARBAGE_CHILD_URL", "http://ai-garbage-child:8002")
GARBAGE_PARENT_URL = os.getenv("AI_GARBAGE_PARENT_URL", "http://ai-garbage-parent:8004")


async def analyze_pothole_report(
    image_url: str,
    description: str,
    latitude: float,
    longitude: float,
    upvotes: int,
    image_bytes: Optional[bytes] = None
) -> Dict:
    """
    Orchestrate pothole analysis pipeline:
    1. Call child models for individual scores
    2. Call parent model for final severity
    """
    try:
        async with httpx.AsyncClient() as client:
            # Read image from local file system
            # image_url is like "/uploads/filename.jpg"
            from pathlib import Path
            
            # Convert URL path to file path
            # Read image
            # Read image
            if image_bytes:
                file_path = None
            elif image_url.startswith("/uploads/"):
                file_path = Path("uploads") / image_url.replace("/uploads/", "")
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        image_bytes = f.read()
                    file_path = None # Found locally
                else:
                    # Not found locally (could happen if DB switch happened mid-flight but unlikely)
                    image_bytes = None
            else:
                # Fallback: try to fetch via HTTP if it's a full URL
                img_resp = await client.get(image_url, timeout=10.0)
                if img_resp.status_code != 200:
                    raise Exception("Failed to fetch image")
                image_bytes = img_resp.content
                file_path = None
            
            # Read image bytes from file if local
            if file_path and file_path.exists():
                with open(file_path, 'rb') as f:
                    image_bytes = f.read()
            elif not file_path:
                # Already fetched via HTTP above
                pass
            else:
                raise Exception(f"Image file not found: {file_path}")
            
            # 1. Analyze Image (YOLO + Depth)
            files = {'image': ('pothole.jpg', image_bytes, 'image/jpeg')}
            img_analysis = await client.post(
                f"{POTHOLE_CHILD_URL}/analyze_image",
                files=files,
                timeout=30.0
            )
            img_data = img_analysis.json()
            spread_score = img_data.get('spread_score', 0.0)
            depth_score = img_data.get('depth_score', 0.0)
            
            # 2. Analyze Sentiment
            sentiment_resp = await client.post(
                f"{POTHOLE_CHILD_URL}/analyze_sentiment",
                json={"text": description},
                timeout=5.0
            )
            sentiment_data = sentiment_resp.json()
            emotion_score = sentiment_data.get('emotion_score', 0.0)
            sentiment_meta = {
                "keywords": sentiment_data.get('keywords', []),
                "sentiment": sentiment_data.get('sentiment', 'UNKNOWN')
            }
            import json
            
            # 3. Analyze Location
            location_resp = await client.post(
                f"{POTHOLE_CHILD_URL}/analyze_location",
                json={"latitude": latitude, "longitude": longitude},
                timeout=10.0
            )
            location_data = location_resp.json()
            location_score = location_data.get('location_score', 0.0)
            location_meta = {
                "nearby_critical_count": location_data.get('nearby_critical_count', 0),
                "schools": location_data.get('schools_nearby', 0),
                "hospitals": location_data.get('hospitals_nearby', 0),
                "is_major_road": location_data.get('is_major_road', False),
                "critical_names": location_data.get('critical_names', [])
            }
            
            # 4. Normalize upvotes
            upvote_score = min(upvotes / 100.0, 1.0)
            
            # 5. Call Parent Model
            parent_resp = await client.post(
                f"{POTHOLE_PARENT_URL}/predict",
                json={
                    "depth_score": depth_score,
                    "spread_score": spread_score,
                    "emotion_score": emotion_score,
                    "location_score": location_score,
                    "upvote_score": upvote_score
                },
                timeout=5.0
            )
            parent_data = parent_resp.json()
            
            return {
                "pothole_depth_score": depth_score,
                "pothole_spread_score": spread_score,
                "emotion_score": emotion_score,
                "location_score": location_score,
                "upvote_score": upvote_score,
                "ai_severity_score": parent_data['severity_score'],
                "ai_severity_level": parent_data['severity_level'],
                "location_meta": json.dumps(location_meta),
                "sentiment_meta": json.dumps(sentiment_meta)
            }
    
    except Exception as e:
        logger.error(f"Pothole analysis failed: {e}")
        return {
            "pothole_depth_score": 0.0,
            "pothole_spread_score": 0.0,
            "emotion_score": 0.0,
            "location_score": 0.0,
            "upvote_score": 0.0,
            "ai_severity_score": 50.0,
            "ai_severity_level": "medium",
            "location_meta": "{}",
            "sentiment_meta": "{}"
        }


async def analyze_garbage_report(
    image_url: str,
    description: str,
    latitude: float,
    longitude: float,
    upvotes: int,
    image_bytes: Optional[bytes] = None
) -> Dict:
    """
    Hybrid Garbage Analysis Pipeline (7-Feature Vector)
    """
    try:
        async with httpx.AsyncClient() as client:
            # -- Image Loading Logic (Keeping existing) --
            from pathlib import Path
            file_path = None
            if image_bytes:
                pass
            elif image_url.startswith("/uploads/"):
                file_path = Path("uploads") / image_url.replace("/uploads/", "")
                if file_path.exists():
                    with open(file_path, 'rb') as f: image_bytes = f.read()
            else:
                 # Fetch remote
                 try:
                     resp = await client.get(image_url, timeout=5.0)
                     if resp.status_code == 200: image_bytes = resp.content
                 except: pass
            
            if not image_bytes and file_path and file_path.exists():
                 with open(file_path, 'rb') as f: image_bytes = f.read()

            if not image_bytes: raise Exception("No image data found")
            
            # --- 1. CHILD: VISUAL (YOLOv8 & CNN) ---
            files = {'image': ('garbage.jpg', image_bytes, 'image/jpeg')}
            
            # A. Object & Coverage (YOLO)
            # We need to seek(0) if re-using bytes potentially? HTTPX handles files usually ok.
            # But let's act sequentially to be safe or re-construct files dict
            yolo_resp = await client.post(f"{GARBAGE_CHILD_URL}/analyze_image", files=files, timeout=30.0)
            yolo_data = yolo_resp.json()
            
            object_count = yolo_data.get('object_count', 0.0)
            coverage_area = yolo_data.get('coverage_area', 0.0)
            detailed_objects = yolo_data.get('detailed_stats', {}) # Capture the 15 object classes

            # B. Scene Dirtiness (CNN) - Re-send image
            files_scene = {'image': ('garbage.jpg', image_bytes, 'image/jpeg')}
            scene_resp = await client.post(f"{GARBAGE_CHILD_URL}/analyze_scene", files=files_scene, timeout=10.0)
            scene_data = scene_resp.json()
            dirtiness_score = scene_data.get('dirtiness_score', 0.0)

            # --- 2. CHILD: TEXT & RISK (NLP) ---
            nlp_resp = await client.post(
                f"{GARBAGE_CHILD_URL}/analyze_sentiment",
                json={"text": description},
                timeout=5.0
            )
            nlp_data = nlp_resp.json()
            text_severity = nlp_data.get('emotion_score', 0.0)
            
            # COMBINED RISK LOGIC (Visal + Text)
            # If "hazardous" items found OR text says "toxic"
            text_risk = nlp_data.get('risk_factor', 0.0)
            visual_risk = 1.0 if detailed_objects.get('hazardous', 0) > 0 else 0.0
            
            risk_factor = max(text_risk, visual_risk)
            found_risks = nlp_data.get('found_risks', [])
            if visual_risk > 0: found_risks.append("SHARP/TOXIC OBJECTS (Visual)")

            # --- 3. CHILD: LOCATION ---
            loc_resp = await client.post(
                f"{GARBAGE_CHILD_URL}/analyze_location",
                json={"latitude": latitude, "longitude": longitude},
                timeout=10.0
            )
            loc_data = loc_resp.json()
            # Mapping location_score to 'location_multiplier' concept
            location_multiplier = loc_data.get('location_score', 0.0) 
            location_meta = {
                "nearby": loc_data.get('nearby_critical_count', 0),
                "schools": loc_data.get('schools_nearby', 0),
                "critical_names": loc_data.get('critical_names', []) # Added Specific Names
            }

            # --- 4. CHILD: SOCIAL ---
            social_score = min(upvotes / 50.0, 1.0) # Normalize upvotes

            # --- 5. PARENT MODEL (7 Inputs) ---
            parent_payload = {
                "object_count": object_count,
                "coverage_area": coverage_area,
                "dirtiness_score": dirtiness_score,
                "location_multiplier": location_multiplier,
                "text_severity": text_severity,
                "social_score": social_score,
                "risk_factor": risk_factor
            }
            
            parent_resp = await client.post(f"{GARBAGE_PARENT_URL}/predict", json=parent_payload, timeout=5.0)
            parent_data = parent_resp.json()
            
            # --- 6. RICH DETAILS FOR FRONTEND (ALL 21 FEATURES) ---
            # We pack all the cool new stats into json structure
            analysis_details = {
                "features": parent_payload, # The 7 Model Inputs
                "risks_detected": found_risks,
                "model_version": "Hybrid-v1",
                "yolo_objects": object_count,
                "object_breakdown": detailed_objects, # The detailed class counts
                "full_21_features": { 
                    **detailed_objects,
                    "risk_flags": len(found_risks), 
                    "location_risk": location_multiplier,
                    "social_urgency": social_score
                }
            }
            import json

            return {
                # Legacy keys for DB compatibility (mapped roughly)
                "garbage_volume_score": coverage_area, 
                "garbage_waste_type_score": risk_factor, # Map risk to waste type slot
                "emotion_score": text_severity,
                "location_score": location_multiplier,
                "upvote_score": social_score,
                
                # Main Results
                "ai_severity_score": parent_data['severity_score'],
                "ai_severity_level": parent_data['severity_level'],
                
                # Rich Metadata
                "location_meta": json.dumps(location_meta),
                "sentiment_meta": json.dumps(analysis_details) # Piggyback on sentiment_meta or create new column if possible. 
                # User asked not to change schema too much, so we'll put it in sentiment_meta which is JSON
            }

    except Exception as e:
        logger.error(f"Hybrid Garbage analysis failed: {e}")
        return {
            "ai_severity_score": 50.0,
            "ai_severity_level": "medium",
            "garbage_volume_score": 0.0,
            "garbage_waste_type_score": 0.0,
            "emotion_score": 0.0,
            "location_score": 0.0,
            "upvote_score": 0.0,
            "location_meta": "{}",
            "sentiment_meta": "{}" 
        }
