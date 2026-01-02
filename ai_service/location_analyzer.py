"""
Location Context Analyzer
Detects nearby sensitive locations and calculates priority multipliers
"""
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class NearbyLocation:
    type: str
    name: str
    distance_m: float

# Priority multipliers for different location types
LOCATION_PRIORITIES = {
    'school': 1.5,
    'kindergarten': 1.5,
    'college': 1.4,
    'university': 1.4,
    'hospital': 1.4,
    'clinic': 1.4,
    'doctors': 1.4,
    'pharmacy': 1.3,
    'park': 1.3,
    'nature_reserve': 1.3,
    'playground': 1.3,
    'residential': 1.1,
    'apartments': 1.1,
    'commercial': 1.0,
    'industrial': 0.9,
}

# OpenStreetMap Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def query_nearby_locations(lat: float, lon: float, radius_m: int = 500) -> List[NearbyLocation]:
    """
    Query OpenStreetMap for nearby points of interest
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_m: Search radius in meters (default 500m)
    
    Returns:
        List of nearby locations with type, name, and distance
    """
    # Overpass QL query for sensitive locations
    overpass_query = f"""
    [out:json][timeout:5];
    (
      node["amenity"~"school|kindergarten|college|university|hospital|clinic|doctors|pharmacy"](around:{radius_m},{lat},{lon});
      node["leisure"~"park|playground|nature_reserve"](around:{radius_m},{lat},{lon});
      way["amenity"~"school|kindergarten|college|university|hospital|clinic|doctors|pharmacy"](around:{radius_m},{lat},{lon});
      way["leisure"~"park|playground|nature_reserve"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    
    try:
        response = requests.post(
            OVERPASS_URL,
            data={'data': overpass_query},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Overpass API error: {response.status_code}")
            return []
        
        data = response.json()
        nearby = []
        
        for element in data.get('elements', []):
            # Get location type from tags
            tags = element.get('tags', {})
            loc_type = tags.get('amenity') or tags.get('leisure')
            
            if not loc_type:
                continue
            
            # Get name
            name = tags.get('name', f"{loc_type.title()}")
            
            # Calculate distance
            elem_lat = element.get('lat') or element.get('center', {}).get('lat')
            elem_lon = element.get('lon') or element.get('center', {}).get('lon')
            
            if elem_lat and elem_lon:
                distance = calculate_distance(lat, lon, elem_lat, elem_lon)
                
                nearby.append(NearbyLocation(
                    type=loc_type,
                    name=name,
                    distance_m=round(distance, 1)
                ))
        
        # Sort by distance
        nearby.sort(key=lambda x: x.distance_m)
        
        return nearby[:5]  # Return top 5 closest
        
    except Exception as e:
        print(f"Error querying nearby locations: {e}")
        return []

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in meters
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Earth radius in meters
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def analyze_location_context(lat: float, lon: float) -> Dict:
    """
    Analyze location context and calculate priority multiplier
    
    Returns:
        Dict containing:
        - nearby_locations: List of nearby sensitive locations
        - priority_multiplier: 0.9-1.5x based on proximity to sensitive areas
        - zone_type: Primary zone type (educational/healthcare/eco/residential/commercial)
        - highest_priority_location: Closest high-priority location
    """
    nearby = query_nearby_locations(lat, lon)
    
    if not nearby:
        # No sensitive locations nearby, assume commercial/default
        return {
            'nearby_locations': [],
            'priority_multiplier': 1.0,
            'zone_type': 'commercial',
            'highest_priority_location': None
        }
    
    # Calculate priority multiplier based on closest high-priority location
    max_multiplier = 1.0
    highest_priority_loc = None
    zone_type = 'commercial'
    
    for loc in nearby:
        loc_priority = LOCATION_PRIORITIES.get(loc.type, 1.0)
        
        # Apply distance decay: full priority within 100m, linear decay to 500m
        if loc.distance_m <= 100:
            distance_factor = 1.0
        elif loc.distance_m <= 500:
            distance_factor = 1.0 - ((loc.distance_m - 100) / 400) * 0.3  # 30% decay
        else:
            distance_factor = 0.7
        
        adjusted_priority = 1.0 + (loc_priority - 1.0) * distance_factor
        
        if adjusted_priority > max_multiplier:
            max_multiplier = adjusted_priority
            highest_priority_loc = loc
            
            # Determine zone type
            if loc.type in ['school', 'kindergarten', 'college', 'university']:
                zone_type = 'educational'
            elif loc.type in ['hospital', 'clinic', 'doctors', 'pharmacy']:
                zone_type = 'healthcare'
            elif loc.type in ['park', 'nature_reserve', 'playground']:
                zone_type = 'eco'
            elif loc.type in ['residential', 'apartments']:
                zone_type = 'residential'
    
    return {
        'nearby_locations': [
            {
                'type': loc.type,
                'name': loc.name,
                'distance_m': loc.distance_m
            }
            for loc in nearby
        ],
        'priority_multiplier': round(max_multiplier, 2),
        'zone_type': zone_type,
        'highest_priority_location': {
            'type': highest_priority_loc.type,
            'name': highest_priority_loc.name,
            'distance_m': highest_priority_loc.distance_m
        } if highest_priority_loc else None
    }
