import requests
import logging
from typing import Dict

logger = logging.getLogger("garbage-child")

def analyze_location(latitude: float, longitude: float) -> Dict:
    """
    Query OpenStreetMap for location context.
    Returns location_score (0-1.0)
    Same logic as pothole service - reusable
    """
    try:
        overpass_url = "http://overpass-api.de/api/interpreter"
        
        query = f"""
        [out:json];
        (
          way(around:10,{latitude},{longitude})["highway"];
          node(around:500,{latitude},{longitude})["amenity"~"school|hospital"];
        );
        out body;
        """
        
        response = requests.post(overpass_url, data={"data": query}, timeout=10)
        data = response.json()
        
        score = 0.0
        elements = data.get('elements', [])
        
        for elem in elements:
            if elem.get('type') == 'way':
                highway_type = elem.get('tags', {}).get('highway', '')
                if highway_type in ['motorway', 'trunk', 'primary', 'secondary']:
                    score += 0.4
                    break
        
        has_school = False
        has_hospital = False
        
        for elem in elements:
            if elem.get('type') == 'node':
                amenity = elem.get('tags', {}).get('amenity', '')
                if amenity == 'school' and not has_school:
                    score += 0.3
                    has_school = True
                elif amenity == 'hospital' and not has_hospital:
                    score += 0.3
                    has_hospital = True
        
        return {
            "location_score": min(score, 1.0),
            "is_major_road": score >= 0.4,
            "near_school": has_school,
            "near_hospital": has_hospital
        }
    
    except Exception as e:
        logger.error(f"OSM query failed: {e}")
        return {"location_score": 0.5, "is_major_road": False, "near_school": False, "near_hospital": False}
