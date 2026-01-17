import torch
from ultralytics import YOLO
from transformers import pipeline
import logging
from pathlib import Path

logger = logging.getLogger("garbage-child")

class GarbageChildModels:
    """Singleton loader for all garbage child models"""
    _instance = None
    _yolo_model = None
    _classifier_pipeline = None
    _sentiment_pipeline = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GarbageChildModels, cls).__new__(cls)
        return cls._instance
    
    def load_models(self):
        """Load all child models at startup"""
        if self._yolo_model is not None:
            logger.info("Models already loaded")
            return
        
        logger.info("Loading garbage child models...")
        
        # 1. YOLO Detection Model for garbage
        try:
            # Using a general object detection model
            # You can replace with a garbage-specific model if available
            self._yolo_model = YOLO("yolov8m.pt")
            logger.info("✓ YOLO detection model loaded")
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")
            raise
        
        # 2. Image Classification for waste type
        try:
            # Using zero-shot classification for waste categorization
            self._classifier_pipeline = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            logger.info("✓ Waste classifier loaded")
        except Exception as e:
            logger.error(f"Failed to load classifier: {e}")
            raise
        
        # 3. Sentiment Analysis Model (same as pothole)
        try:
            self._sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("✓ Sentiment analysis model loaded")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise
        
        logger.info("All garbage child models loaded successfully")
    
    def get_yolo(self):
        if self._yolo_model is None:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self._yolo_model
    
    def get_classifier(self):
        if self._classifier_pipeline is None:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self._classifier_pipeline
    
    def get_sentiment_pipeline(self):
        if self._sentiment_pipeline is None:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self._sentiment_pipeline


# Global singleton instance
garbage_models = GarbageChildModels()
