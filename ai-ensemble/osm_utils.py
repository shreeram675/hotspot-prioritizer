import requests
import logging

logger = logging.getLogger("ai-ensemble")

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

def get_location_context(lat: float, lon: float) -> dict:
    """
    Queries Overpass API to find nearby sensitive areas and road type.
    Returns a dict with context scores.
    """
    # 500m radius check for schools and hospitals
    query = f"""
    [out:json];
    (
      node["amenity"="school"](around:500, {lat}, {lon});
      way["amenity"="school"](around:500, {lat}, {lon});
      relation["amenity"="school"](around:500, {lat}, {lon});
      node["amenity"="hospital"](around:500, {lat}, {lon});
      way["amenity"="hospital"](around:500, {lat}, {lon});
      relation["amenity"="hospital"](around:500, {lat}, {lon});
      way["highway"~"motorway|trunk|primary|secondary"](around:50, {lat}, {lon});
    );
    out center;
    """
    
    context = {
        "near_school": False,
        "near_hospital": False,
        "is_major_road": False,
        "score": 0.0
    }

    try:
        response = requests.get(OVERPASS_URL, params={'data': query}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for element in data.get("elements", []):
                tags = element.get("tags", {})
                
                if tags.get("amenity") == "school":
                    context["near_school"] = True
                if tags.get("amenity") == "hospital":
                    context["near_hospital"] = True
                
                highway = tags.get("highway")
                if highway in ["motorway", "trunk", "primary", "secondary"]:
                    context["is_major_road"] = True
        else:
            logger.warning(f"Overpass API returned status {response.status_code}")

    except Exception as e:
        logger.error(f"Error querying Overpass API: {e}")
        # Fail gracefully, return neutral context
        return context

    # Calculate Score
    score = 0.0
    if context["is_major_road"]:
        score += 0.4
    if context["near_school"]:
        score += 0.3
    if context["near_hospital"]:
        score += 0.3
    
    # Cap at 1.0 (though logic allows 1.0 exactly here)
    context["score"] = min(score, 1.0)
    
    return context
