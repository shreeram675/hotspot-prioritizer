"""
YOLO-based Object Detection Module for Garbage Analysis
Uses YOLOv8n pretrained on COCO dataset to detect garbage-related objects
"""
from ultralytics import YOLO
from typing import Dict, List, Tuple
import numpy as np
from PIL import Image
import io

# Singleton model instance
_yolo_model = None

# COCO classes that are garbage-related or indicate waste
GARBAGE_RELATED_CLASSES = {
    39: 'bottle',
    40: 'wine glass',
    41: 'cup',
    42: 'fork',
    43: 'knife',
    44: 'spoon',
    45: 'bowl',
    46: 'banana',
    47: 'apple',
    48: 'sandwich',
    49: 'orange',
    50: 'broccoli',
    51: 'carrot',
    52: 'hot dog',
    53: 'pizza',
    54: 'donut',
    55: 'cake',
    # Containers and packaging
    73: 'book',
    76: 'scissors',
    84: 'book',
    85: 'clock',
    86: 'vase',
}

# Classes indicating bins or containers (positive indicators)
BIN_CLASSES = {
    # These would be trash cans, but COCO doesn't have explicit trash can class
    # We'll use backpack, handbag, suitcase as proxy for containers
    24: 'backpack',
    26: 'handbag',
    28: 'suitcase',
}

def get_yolo_model():
    """Load and cache YOLOv8n model"""
    global _yolo_model
    if _yolo_model is None:
        print("Loading YOLOv8n model (COCO pretrained)...")
        _yolo_model = YOLO('yolov8n.pt')  # Nano variant for faster CPU inference
        print("YOLOv8n model loaded successfully")
    return _yolo_model

def detect_garbage_objects(image_bytes: bytes) -> Dict:
    """
    Detect garbage-related objects in an image using YOLO
    
    Returns:
        Dict containing:
        - object_count: Number of garbage-related objects detected
        - coverage_area: Ratio of image covered by garbage (0-1)
        - density: Objects per unit area
        - has_overflow: Boolean indicating potential overflow/clustering
        - detections: List of detected objects with details
    """
    model = get_yolo_model()
    
    # Load image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_width, img_height = image.size
    total_area = img_width * img_height
    
    # Run inference
    results = model(image, verbose=False)
    
    # Process detections
    garbage_objects = []
    total_garbage_area = 0
    bin_detected = False
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            # Only consider high-confidence detections
            if confidence < 0.3:
                continue
            
            # Check if it's a garbage-related class
            if cls_id in GARBAGE_RELATED_CLASSES:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                bbox_area = (x2 - x1) * (y2 - y1)
                
                garbage_objects.append({
                    'class_id': cls_id,
                    'class_name': GARBAGE_RELATED_CLASSES[cls_id],
                    'confidence': confidence,
                    'bbox': [x1, y1, x2, y2],
                    'area': bbox_area
                })
                
                total_garbage_area += bbox_area
            
            elif cls_id in BIN_CLASSES:
                bin_detected = True
    
    # Calculate metrics
    object_count = len(garbage_objects)
    coverage_area = min(total_garbage_area / total_area, 1.0) if total_area > 0 else 0.0
    density = object_count / (total_area / 1000000) if total_area > 0 else 0.0  # objects per megapixel
    
    # Detect overflow: high object count + high coverage
    has_overflow = object_count > 10 and coverage_area > 0.3
    
    # Detect open dump: very high object count or coverage
    is_open_dump = object_count > 20 or coverage_area > 0.5
    
    return {
        'object_count': object_count,
        'coverage_area': coverage_area,
        'density': density,
        'has_overflow': has_overflow,
        'is_open_dump': is_open_dump,
        'bin_detected': bin_detected,
        'detections': garbage_objects[:10]  # Limit to top 10 for response size
    }

def calculate_garbage_spread(detections: List[Dict]) -> float:
    """
    Calculate how spread out the garbage is (clustering metric)
    Returns value 0-1, where 1 means highly clustered
    """
    if len(detections) < 2:
        return 0.0
    
    # Calculate centroid of each detection
    centroids = []
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        centroids.append([cx, cy])
    
    centroids = np.array(centroids)
    
    # Calculate average distance from mean centroid
    mean_centroid = centroids.mean(axis=0)
    distances = np.linalg.norm(centroids - mean_centroid, axis=1)
    avg_distance = distances.mean()
    
    # Normalize (lower distance = more clustered)
    # Assuming max reasonable distance is 1000 pixels
    clustering_score = max(0, 1 - (avg_distance / 1000))
    
    return clustering_score
