import torch
from ultralytics import YOLO
from transformers import pipeline
import logging
from pathlib import Path

logger = logging.getLogger("pothole-child")

class PotholeChildModels:
    """Singleton loader for all pothole child models"""
    _instance = None
    _yolo_model = None
    _depth_pipeline = None
    _sentiment_pipeline = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PotholeChildModels, cls).__new__(cls)
        return cls._instance
    
    def load_models(self):
        """Load all child models at startup"""
        if self._yolo_model is not None:
            logger.info("Models already loaded")
            return
        
        logger.info("Loading pothole child models...")
        
        # 1. YOLO Segmentation Model
        try:
            self._yolo_model = YOLO("keremberke/yolov8m-pothole-segmentation")
            logger.info("✓ YOLO segmentation model loaded")
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")
            raise
        
        # 2. Depth Estimation Model
        try:
            self._depth_pipeline = pipeline(
                "depth-estimation",
                model="LiheYoung/depth-anything-small-hf"
            )
            logger.info("✓ Depth estimation model loaded")
        except Exception as e:
            logger.error(f"Failed to load depth model: {e}")
            raise
        
        # 3. Sentiment Analysis Model
        try:
            self._sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("✓ Sentiment analysis model loaded")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise
        
        logger.info("All pothole child models loaded successfully")
    
    def get_yolo(self):
        if self._yolo_model is None:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self._yolo_model
    
    def get_depth_pipeline(self):
        if self._depth_pipeline is None:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self._depth_pipeline
    
    def get_sentiment_pipeline(self):
        if self._sentiment_pipeline is None:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        return self._sentiment_pipeline


# Global singleton instance
pothole_models = PotholeChildModels()
