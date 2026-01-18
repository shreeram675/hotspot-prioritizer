import logging
import os
import sys

# EXTERNAL_MODELS_DIR = Path("/external_models") # Not using local models anymore

logger = logging.getLogger("garbage-child")

class GarbageChildModels:
    """
    Hybrid Model Loader (API VERSION):
    - NO LOCAL MODELS (to avoid heavy install)
    - Uses Hugging Face Inference API for all child tasks (Object, Scene, NLP)
    - Falls back to simulation if API fails/no token
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GarbageChildModels, cls).__new__(cls)
            cls._instance.device = "cloud"
        return cls._instance
    
    def load_models(self):
        """No local loading needed for API mode"""
        logger.info("Garbage Child running in CLOUD/API-ONLY mode. No local weights loaded.")

    # --- HF API CONFIG ---
    HF_API_BASE = "https://api-inference.huggingface.co/models"
    HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "") # Ensure this is set in docker-compose if user has one
    
    # 1. Object Detection (YOLO/DETR)
    def get_object_detection_pipeline(self):
        # Using a reliable public model for general objects (COCO)
        return f"{self.HF_API_BASE}/facebook/detr-resnet-50"

    # 2. Scene Classification (ResNet/ViT)
    def get_scene_classifier_pipeline(self):
        # Using a model good for scene/nature/urban classification
        return f"{self.HF_API_BASE}/google/vit-base-patch16-224"

    # 3. Sentiment/NLP
    def get_sentiment_pipeline(self):
         return f"{self.HF_API_BASE}/distilbert-base-uncased-finetuned-sst-2-english"

    def query_api(self, api_url, data, headers=None):
        import requests
        if headers is None: headers = {}
        if self.HF_API_TOKEN: 
            headers["Authorization"] = f"Bearer {self.HF_API_TOKEN}"
        
        try:
            # For image data (bytes), we send raw body
            if isinstance(data, bytes):
                headers["Content-Type"] = "application/octet-stream"
                response = requests.post(api_url, headers=headers, data=data, timeout=8)
            else:
                # JSON/Dict
                response = requests.post(api_url, headers=headers, json=data, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"API Error {api_url}: {response.status_code} - {response.text}")
                return None
                
            return response.json()
        except Exception as e:
            logger.error(f"API Connection Failed: {e}")
            return None

# Global singleton instance
garbage_models = GarbageChildModels()
