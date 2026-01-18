import requests
import logging
from pathlib import Path
import os

logger = logging.getLogger("pothole-child")

# HuggingFace API configuration
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")  # Optional, for higher rate limits
HF_API_BASE = "https://api-inference.huggingface.co/models"

class PotholeChildModels:
    """API-based model inference using HuggingFace Inference API"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PotholeChildModels, cls).__new__(cls)
        return cls._instance
    
    def load_models(self):
        """No models to load - using API"""
        logger.info("Using HuggingFace Inference API (no local models)")
        logger.info("All pothole child models ready (API mode)")
    
    def get_yolo(self):
        """Returns API endpoint for YOLO"""
        return f"{HF_API_BASE}/facebook/detr-resnet-50"
    
    def get_depth_pipeline(self):
        """Returns API endpoint for depth estimation"""
        return f"{HF_API_BASE}/Intel/dpt-large"
    
    def get_sentiment_pipeline(self):
        """Returns API endpoint for sentiment analysis"""
        return f"{HF_API_BASE}/distilbert-base-uncased-finetuned-sst-2-english"
    
    def query_api(self, api_url, data, headers=None):
        """Query HuggingFace Inference API"""
        if headers is None:
            headers = {}
        if HF_API_TOKEN:
            headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
        
        response = requests.post(api_url, headers=headers, data=data)
        return response.json()


# Global singleton instance
pothole_models = PotholeChildModels()
