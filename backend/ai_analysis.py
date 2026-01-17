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
    upvotes: int
) -> Dict:
    """
    Orchestrate pothole analysis pipeline:
    1. Call child models for individual scores
    2. Call parent model for final severity
    """
    try:
        async with httpx.AsyncClient() as client:
            # Fetch image
            img_resp = await client.get(image_url, timeout=10.0)
            if img_resp.status_code != 200:
                raise Exception("Failed to fetch image")
            
            image_bytes = img_resp.content
            
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
            
            # 3. Analyze Location
            location_resp = await client.post(
                f"{POTHOLE_CHILD_URL}/analyze_location",
                json={"latitude": latitude, "longitude": longitude},
                timeout=10.0
            )
            location_data = location_resp.json()
            location_score = location_data.get('location_score', 0.0)
            
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
                "ai_severity_level": parent_data['severity_level']
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
            "ai_severity_level": "medium"
        }


async def analyze_garbage_report(
    image_url: str,
    description: str,
    latitude: float,
    longitude: float,
    upvotes: int
) -> Dict:
    """
    Orchestrate garbage analysis pipeline:
    1. Call child models for individual scores
    2. Call parent model for final severity
    """
    try:
        async with httpx.AsyncClient() as client:
            # Fetch image
            img_resp = await client.get(image_url, timeout=10.0)
            if img_resp.status_code != 200:
                raise Exception("Failed to fetch image")
            
            image_bytes = img_resp.content
            
            # 1. Analyze Image (YOLO + Classifier)
            files = {'image': ('garbage.jpg', image_bytes, 'image/jpeg')}
            img_analysis = await client.post(
                f"{GARBAGE_CHILD_URL}/analyze_image",
                files=files,
                timeout=30.0
            )
            img_data = img_analysis.json()
            volume_score = img_data.get('volume_score', 0.0)
            waste_type_score = img_data.get('waste_type_score', 0.0)
            
            # 2. Analyze Sentiment
            sentiment_resp = await client.post(
                f"{GARBAGE_CHILD_URL}/analyze_sentiment",
                json={"text": description},
                timeout=5.0
            )
            sentiment_data = sentiment_resp.json()
            emotion_score = sentiment_data.get('emotion_score', 0.0)
            
            # 3. Analyze Location
            location_resp = await client.post(
                f"{GARBAGE_CHILD_URL}/analyze_location",
                json={"latitude": latitude, "longitude": longitude},
                timeout=10.0
            )
            location_data = location_resp.json()
            location_score = location_data.get('location_score', 0.0)
            
            # 4. Normalize upvotes
            upvote_score = min(upvotes / 100.0, 1.0)
            
            # 5. Call Parent Model
            parent_resp = await client.post(
                f"{GARBAGE_PARENT_URL}/predict",
                json={
                    "volume_score": volume_score,
                    "waste_type_score": waste_type_score,
                    "emotion_score": emotion_score,
                    "location_score": location_score,
                    "upvote_score": upvote_score
                },
                timeout=5.0
            )
            parent_data = parent_resp.json()
            
            return {
                "garbage_volume_score": volume_score,
                "garbage_waste_type_score": waste_type_score,
                "emotion_score": emotion_score,
                "location_score": location_score,
                "upvote_score": upvote_score,
                "ai_severity_score": parent_data['severity_score'],
                "ai_severity_level": parent_data['severity_level']
            }
    
    except Exception as e:
        logger.error(f"Garbage analysis failed: {e}")
        return {
            "garbage_volume_score": 0.0,
            "garbage_waste_type_score": 0.0,
            "emotion_score": 0.0,
            "location_score": 0.0,
            "upvote_score": 0.0,
            "ai_severity_score": 50.0,
            "ai_severity_level": "medium"
        }
