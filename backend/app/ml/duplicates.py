from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from .. import models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# from geopy.distance import geodesic # Removed to avoid dependency issues

def check_duplicate(db: Session, description: str, lat: float = None, lon: float = None, threshold: float = 0.3) -> list[dict]:
    """
    Duplicate detection using Spatial Filter + TF-IDF.
    1. Finds reports within 50 meters.
    2. Checks semantic similarity on those reports.
    """
    if not description:
        return []
        
    candidates = []
    
    # 1. Spatial Filter (if lat/lon provided)
    if lat is not None and lon is not None:
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        
        # Find reports within 50 meters
        candidates = db.query(models.Report).filter(
            models.Report.description != None,
            func.ST_DWithin(models.Report.location.cast(Geography), point.cast(Geography), 50)
        ).all()
    
    # Fallback: If no location provided, or no candidates found? 
    # If location WAS provided but no neighbors, then it's definitely unique spatially. 
    # But if location WAS NOT provided (legacy call?), we might want to check recent global.
    if not candidates and (lat is None or lon is None):
        # Fallback to last 100 recent reports (Text-only check)
        candidates = db.query(models.Report).filter(models.Report.description != None).order_by(models.Report.created_at.desc()).limit(100).all()

    if not candidates:
        return []

    duplicates = []
    
    # Prepare corpus: [current_desc] + [candidate_descs]
    corpus = [description] + [r.description for r in candidates]
    
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calculate cosine similarity of the first item (current) against all others
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Flatten result
        scores = cosine_sim[0]
        
        for idx, score in enumerate(scores):
            if score >= threshold:
                report = candidates[idx]
                
                # Calculate Distance if lat/lon provided
                dist_m = 0
                if lat is not None and lon is not None:
                    # Parse geometry
                    shape = to_shape(report.location)
                    # Simple distance approx or accurate geodesic
                    # Using geopy if available, else manual
                    # Let's use simple manual approximation or assume 0 if package missing.
                    # Actually, reports.py uses ST_Distance.
                    # Since we are iterating python objects, let's use a quick approx if dependencies issues, 
                    # but I added 'geopy' to import? Wait, is geopy installed? 
                    # Checking requirements.txt might be needed. 
                    # Safest is to use Shapely's distance if projected, but we are in LatLon.
                    # Let's use logic from reports.py: query returns distance.
                    # But here we already queried objects. 
                    # Let's just return 0 or approx distance.
                    # Better: Re-query with distance? No.
                    # Let's allow distance_m to be 0 if not calculated perfectly here, 
                    # or use basic Haversine implementation inline to avoid deps.
                    pass 
                
                # Inline Haversine for safety
                if lat is not None and lon is not None:
                    r_shape = to_shape(report.location)
                    from math import radians, cos, sin, asin, sqrt
                    lon1, lat1, lon2, lat2 = map(radians, [lon, lat, r_shape.x, r_shape.y])
                    dlon = lon2 - lon1 
                    dlat = lat2 - lat1 
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * asin(sqrt(a)) 
                    r = 6371 * 1000 # Radius of earth in meters
                    dist_m = c * r
                else:
                    dist_m = -1

                duplicates.append({
                    "report_id": report.report_id,
                    "title": report.title,
                    "similarity": round(float(score), 2),
                    "reason": "Similar functionality/description nearby",
                    "upvote_count": report.upvote_count,
                    "distance_m": round(dist_m, 1)
                })
        
        # Sort by similarity
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
    except Exception as e:
        print(f"Error in duplicate detection: {e}")
        
    return duplicates
