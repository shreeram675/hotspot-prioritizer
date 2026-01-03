from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from .. import models, schemas, database
from ..deps.roles import get_current_user
import shutil
import os
import uuid
from ..ml.classifier import predict_severity
from ..ml.duplicates import check_duplicate
import httpx

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.post("/", response_model=schemas.ReportResponse)
def create_report(
    title: str = Form(...),
    category: str = Form(...),
    description: str = Form(None),
    lat: float = Form(...),
    lon: float = Form(...),
    road_importance: int = Form(1), # Default 1 (Street)
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Handle Image Upload
    image_url = None
    if image:
        # Ensure media directory exists
        os.makedirs("media", exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"media/{filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        image_url = f"/media/{filename}"

    # Create geometry from lat/lon
    location_wkt = f'POINT({lon} {lat})'
    
    new_report = models.Report(
        user_id=current_user.user_id,
        category=category,
        title=title,
        description=description,
        location=location_wkt,
        road_importance=road_importance
    )

    # ML: Predict Severity & Category using AI Service with Context
    ai_severity = None
    ai_category = None
    ai_analysis_data = {}
    location_context_data = None
    text_sentiment_data = None
    
    if image_url:
        try:
            # Call AI Service for comprehensive severity analysis with context
            with open(file_path, "rb") as f:
                img_bytes = f.read()
                
            files = {'file': (filename, img_bytes, 'image/jpeg')}
            
            # Prepare context data for AI service
            data = {
                'lat': lat,
                'lon': lon,
                'description': description or '',
                'upvote_count': 0  # Will be updated as upvotes come in
            }
            
            # Try new severity analysis endpoint with context
            ai_service_host = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
            ai_url = f"{ai_service_host}/analyze-severity"
            
            with httpx.Client(timeout=15.0) as client:  # Increased timeout for NLP + location
                try:
                    resp = client.post(ai_url, files=files, data=data)
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        
                        # Extract comprehensive AI analysis
                        ai_analysis_data = {
                            'severity_score': result.get('severity_score'),
                            'severity_category': result.get('severity_category'),
                            'object_count': result.get('object_detection', {}).get('object_count'),
                            'coverage_area': result.get('object_detection', {}).get('coverage_area'),
                            'scene_dirtiness': result.get('scene_classification', {}).get('dirtiness_score'),
                            'confidence_explanation': result.get('explanation')
                        }
                        
                        # Extract location context if available
                        if 'location_context' in result:
                            location_context_data = result['location_context']
                        
                        # Extract text sentiment if available
                        if 'text_analysis' in result:
                            text_sentiment_data = result['text_analysis']
                        
                        # Extract waste classification if available
                        waste_classification_data = result.get('waste_classification')
                        
                        # Map AI severity category to our severity levels
                        ai_cat = result.get('severity_category')
                        if ai_cat in ['Extreme', 'High']:
                            ai_severity = 'High'
                        elif ai_cat == 'Medium':
                            ai_severity = 'Medium'
                        else:
                            ai_severity = 'Low'
                        
                        # Determine category based on detections
                        obj_detection = result.get('object_detection', {})
                        if obj_detection.get('object_count', 0) > 0:
                            ai_category = "Garbage / Sanitation"
                        
                        print(f"AI Severity Analysis: {ai_cat} (Score: {result.get('severity_score')})")
                        if location_context_data:
                            print(f"  Location Priority: {location_context_data.get('priority_multiplier')}x ({location_context_data.get('zone_type')})")
                        if text_sentiment_data:
                            print(f"  Text Urgency: {text_sentiment_data.get('urgency_level')}")
                        
                except Exception as e:
                    print(f"New AI endpoint failed, falling back to legacy: {e}")
                    # Fallback to legacy /detect endpoint
                    ai_url_legacy = f"{ai_service_host}/detect"
                    resp = client.post(ai_url_legacy, files={'file': (filename, img_bytes, 'image/jpeg')})
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        if result.get("is_garbage"):
                            cat = result.get("detected_category")
                            if cat == "Pothole":
                                ai_category = "Pothole / Road Defect"
                            else:
                                ai_category = "Garbage / Sanitation"
                            
                            if result.get("confidence", 0) > 0.8:
                                ai_severity = "High"
                            else:
                                ai_severity = "Medium"
                                
        except Exception as e:
            print(f"AI Service Error: {e}")

    # Set Category (Prioritize AI)
    final_category = ai_category if ai_category else category
    new_report.category = final_category
    
    # Set Severity
    if ai_severity:
        new_report.severity = ai_severity
    elif image_url:
        # Fallback to local heuristic if AI didn't return severity or failed
        abs_path = os.path.abspath(file_path)
        new_report.severity = predict_severity(abs_path)
    else:
        new_report.severity = "Medium" # Default
    
    # Store AI analysis data if available
    if ai_analysis_data:
        new_report.ai_severity_score = ai_analysis_data.get('severity_score')
        new_report.ai_severity_category = ai_analysis_data.get('severity_category')
        new_report.ai_object_count = ai_analysis_data.get('object_count')
        new_report.ai_coverage_area = ai_analysis_data.get('coverage_area')
        new_report.ai_scene_dirtiness = ai_analysis_data.get('scene_dirtiness')
        new_report.ai_confidence_explanation = ai_analysis_data.get('confidence_explanation')
    
    # Store location context data if available
    if location_context_data:
        new_report.location_context = location_context_data
        new_report.location_priority_multiplier = location_context_data.get('priority_multiplier', 1.0)
    
    # Store text sentiment data if available
    if text_sentiment_data:
        new_report.text_sentiment_score = text_sentiment_data.get('sentiment_score')
        new_report.text_urgency_keywords = ', '.join(text_sentiment_data.get('keywords', []))
        new_report.text_emotion_category = text_sentiment_data.get('emotion')
    
    # Store waste classification data if available
    if 'waste_classification_data' in locals() and waste_classification_data:
        new_report.waste_primary_type = waste_classification_data.get('primary_type')
        new_report.waste_composition = waste_classification_data.get('waste_composition')
        new_report.is_hazardous_waste = waste_classification_data.get('is_hazardous', False)
        recommendations = waste_classification_data.get('recommendations', [])
        new_report.waste_disposal_recommendations = '; '.join(recommendations) if recommendations else None
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # Save image if present
    if image_url:
        new_image = models.ReportImage(
            report_id=new_report.report_id,
            file_path=image_url
        )
        db.add(new_image)
        db.commit()
    
    return {
        "report_id": new_report.report_id,
        "user_id": new_report.user_id,
        "title": new_report.title,
        "category": new_report.category,
        "description": new_report.description,
        "images": [image_url] if image_url else [],
        "lat": lat,
        "lon": lon,
        "upvote_count": new_report.upvote_count,
        "status": new_report.status,
        "status": new_report.status,
        "severity": new_report.severity,
        "road_importance": new_report.road_importance,
        "created_at": new_report.created_at
    }

@router.post("/check-duplicates", response_model=list[dict])
def check_duplicates_endpoint(
    description: str = Form(...),
    lat: float = Form(None),
    lon: float = Form(None),
    db: Session = Depends(database.get_db)
):
    """
    Check for potential duplicates based on description AND location.
    Returns a list of similar reports within 50m or globally if no location.
    """
    duplicates = check_duplicate(db, description, lat, lon)
    return duplicates

@router.post("/{report_id}/upvote", response_model=dict)
def upvote_report(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if report exists
    report = db.query(models.Report).filter(models.Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if already upvoted
    existing_upvote = db.query(models.Upvote).filter(
        models.Upvote.report_id == report_id,
        models.Upvote.user_id == current_user.user_id
    ).first()
    
    if existing_upvote:
        # User already upvoted, do nothing or return error? 
        # Spec says "ON CONFLICT DO NOTHING", so we can just return success without incrementing
        return {"ok": True, "upvote_count": report.upvote_count}
    
    # Create upvote
    new_upvote = models.Upvote(report_id=report_id, user_id=current_user.user_id)
    db.add(new_upvote)
    
    # Increment count
    report.upvote_count += 1
    db.commit()
    
    return {"ok": True, "upvote_count": report.upvote_count}

    return {"ok": True, "upvote_count": report.upvote_count}

@router.delete("/{report_id}/unvote", response_model=dict)
def unvote_report(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if report exists
    report = db.query(models.Report).filter(models.Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if upvoted
    existing_upvote = db.query(models.Upvote).filter(
        models.Upvote.report_id == report_id,
        models.Upvote.user_id == current_user.user_id
    ).first()
    
    if not existing_upvote:
        return {"ok": True, "upvote_count": report.upvote_count}
    
    # Remove upvote
    db.delete(existing_upvote)
    
    # Decrement count
    if report.upvote_count > 0:
        report.upvote_count -= 1
    db.commit()
    
    return {"ok": True, "upvote_count": report.upvote_count}

from typing import Optional
from ..deps.roles import get_current_user_optional

@router.get("/nearby", response_model=list[dict])
def get_nearby_reports(
    lat: float,
    lon: float,
    radius_m: int = 500,
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    # Create point from input lat/lon
    point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    
    # Cast to Geography for accurate distance in meters
    results = db.query(
        models.Report,
        func.ST_Distance(models.Report.location.cast(Geography), point.cast(Geography)).label("distance_m")
    ).filter(
        func.ST_DWithin(models.Report.location.cast(Geography), point.cast(Geography), radius_m)
    ).all()
    
    # Get user's upvotes if logged in
    upvoted_report_ids = set()
    if current_user:
        upvotes = db.query(models.Upvote.report_id).filter(models.Upvote.user_id == current_user.user_id).all()
        upvoted_report_ids = {u.report_id for u in upvotes}
    
    # Format response
    response = []
    for report, distance in results:
        shape = to_shape(report.location)
        
        # Get images
        images = [img.file_path for img in report.images]

        response.append({
            "report_id": report.report_id,
            "title": report.title,
            "category": report.category,
            "lat": shape.y,
            "lon": shape.x,
            "upvote_count": report.upvote_count,
            "distance_m": distance,
            "images": images,
            "is_upvoted": report.report_id in upvoted_report_ids
        })
        
    return response

@router.get("/{report_id}", response_model=dict)
def get_report_detail(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """Get detailed information about a specific report"""
    report = db.query(models.Report).filter(models.Report.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Get report creator info
    creator = db.query(models.User).filter(models.User.user_id == report.user_id).first()
    
    # Check if current user has upvoted
    is_upvoted = False
    if current_user:
        existing_upvote = db.query(models.Upvote).filter(
            models.Upvote.report_id == report_id,
            models.Upvote.user_id == current_user.user_id
        ).first()
        is_upvoted = existing_upvote is not None
    
    # Get location coordinates
    shape = to_shape(report.location)
    
    # Get all images
    images = [img.file_path for img in report.images]
    
    return {
        "report_id": report.report_id,
        "title": report.title,
        "description": report.description,
        "category": report.category,
        "lat": shape.y,
        "lon": shape.x,
        "images": images,
        "upvote_count": report.upvote_count,
        "status": report.status,
        "created_at": report.created_at,
        "created_by": {
            "user_id": creator.user_id,
            "name": creator.name,
            "email": creator.email
        } if creator else None,
        "is_upvoted": is_upvoted,
        "road_importance": report.road_importance
    }

from ..deps.roles import require_role

@router.get("/", response_model=list[schemas.ReportResponse])
def get_reports(
    scope: str = "all", # all, mine
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    query = db.query(models.Report)
    
    if scope == "mine":
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required for scope='mine'")
        query = query.filter(models.Report.user_id == current_user.user_id)
    
    if status:
        query = query.filter(models.Report.status == status)
        
    reports = query.order_by(models.Report.created_at.desc()).offset(skip).limit(limit).all()
    
    # Enrich with is_upvoted
    upvoted_ids = set()
    if current_user:
        upvotes = db.query(models.Upvote.report_id).filter(models.Upvote.user_id == current_user.user_id).all()
        upvoted_ids = {u.report_id for u in upvotes}
        
    results = []
    for r in reports:
        # Convert to schema compatible dict
        r_dict = {
            "report_id": r.report_id,
            "user_id": r.user_id,
            "title": r.title,
            "category": r.category,
            "description": r.description,
            "lat": to_shape(r.location).y if r.location is not None else 0.0,
            "lon": to_shape(r.location).x if r.location is not None else 0.0,
            "images": [img.file_path for img in r.images],
            "upvote_count": r.upvote_count,
            "status": r.status,
            "created_at": r.created_at,
            "is_upvoted": r.report_id in upvoted_ids,
            "road_importance": r.road_importance or 1,
            "ai_severity_score": r.ai_severity_score,
            "ai_severity_category": r.ai_severity_category
        }
        results.append(r_dict)
        
    return results

@router.patch("/{report_id}/status", response_model=schemas.ReportResponse)
def update_report_status(
    report_id: int,
    update: schemas.ReportStatusUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    report = db.query(models.Report).filter(models.Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Record history
    history = models.ReportHistory(
        report_id=report_id,
        old_status=report.status,
        new_status=update.status,
        note=update.note,
        changed_by=current_user.user_id
    )
    db.add(history)
    
    # Update status
    report.status = update.status
    db.commit()
    db.refresh(report)
    
    # Return enriched response (simplified for now, assuming admin doesn't need is_upvoted in this response or it's false)
    return {
        "report_id": report.report_id,
        "user_id": report.user_id,
        "title": report.title,
        "category": report.category,
        "description": report.description,
        "lat": to_shape(report.location).y,
        "lon": to_shape(report.location).x,
        "images": [img.file_path for img in report.images],
        "upvote_count": report.upvote_count,
        "status": report.status,
        "created_at": report.created_at,
        "is_upvoted": False, # Context specific, maybe fetch if needed
        "road_importance": report.road_importance
    }

@router.post("/{report_id}/assign", response_model=dict)
def assign_report(
    report_id: int,
    assignment: schemas.AssignmentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    report = db.query(models.Report).filter(models.Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    new_assignment = models.Assignment(
        report_id=report_id,
        staff_name=assignment.staff_name,
        staff_phone=assignment.staff_phone,
        assigned_by=current_user.user_id,
        expected_resolution_date=assignment.expected_resolution_date,
        status="assigned"
    )
    db.add(new_assignment)
    
    # Auto-update status to 'in_progress' if it was 'open'
    if report.status == "open":
        report.status = "in_progress"
        # Add history
        history = models.ReportHistory(
            report_id=report_id,
            old_status="open",
            new_status="in_progress",
            note=f"Assigned to {assignment.staff_name}",
            changed_by=current_user.user_id
        )
        db.add(history)
        
    db.commit()
    return {"ok": True, "message": "Assignment created"}
