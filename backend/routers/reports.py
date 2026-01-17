from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from typing import List, Optional
import httpx
import os
from database import get_db
from models import Report, User, UserRole, ReportStatus, ReportSeverity, ReportPriority, Department, FieldTeam
from schemas import ReportCreate, ReportResponse, ReportUpdate
from routers.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

# AI Service URLs
AI_DUPLICATE_URL = os.getenv("AI_DUPLICATE_URL", "http://ai-duplicate:9001")

async def auto_assign_department(category: str, db: AsyncSession) -> Optional[int]:
    """Map category to department."""
    # Simple mapping for MVP
    mapping = {
        "pothole": "Roads",
        "street_light": "Electrical",
        "garbage": "Sanitation",
        "flooding": "Drainage",
        "graffiti": "Sanitation"
    }
    dept_name = mapping.get(category)
    if dept_name:
        result = await db.execute(select(Department).where(Department.name == dept_name))
        dept = result.scalars().first()
        if dept:
            return dept.id
    return None

async def predict_severity(text: str) -> ReportSeverity:
    """Predict severity using AI service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_DUPLICATE_URL}/predict_severity",
                json={"text": text},
                timeout=5.0
            )
            if response.status_code == 200:
                result = response.json()
                severity_str = result['severity']
                # Map string to enum
                if severity_str in ReportSeverity.__members__:
                    return ReportSeverity[severity_str]
    except Exception as e:
        print(f"Severity prediction failed: {e}")

    # Fallback logic
    text_lower = text.lower()
    if "danger" in text_lower or "accident" in text_lower or "huge" in text_lower:
        return ReportSeverity.critical
    if "urgent" in text_lower:
        return ReportSeverity.high
    return ReportSeverity.medium

@router.post("/", response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create WKT point from lat/lon
    # Note: PostGIS uses (lon, lat) order for points
    location_wkt = f"POINT({report.longitude} {report.latitude})"
    
    # Auto-predict category if not provided or is generic
    predicted_category = report.category
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_DUPLICATE_URL}/predict_category",
                json={"text": f"{report.title}. {report.description}"},
                timeout=10.0
            )
            if response.status_code == 200:
                result = response.json()
                if result['confidence'] > 0.6:  # Only use if confident
                    predicted_category = result['category']
    except Exception as e:
        print(f"Category prediction failed: {e}")
    

    
    # Auto-assign Department
    department_id = await auto_assign_department(predicted_category, db)
    
    # Call AI Ensemble Service
    ai_scores = {}
    ai_details_str = None
    
    # AI Service URL (Localhost port 8002)
    AI_ENSEMBLE_URL = os.getenv("AI_ENSEMBLE_URL", "http://localhost:8002")

    if report.image_url:
        try:
            # We need to download the image first to send it to the AI service
            # Or if image_url is a local path (upload), handle accordingly.
            # Assuming image_url is accessible via http or is a base64? 
            # In a real app, we'd pass the file directly from the upload.
            # For this MVP, let's assume the frontend sends the file in a separate multipart form if we strictly followed that.
            # BUT: report.image_url suggests it's already uploaded to cloud/server.
            
            # Use a dummy text analysis if image is not readily available as bytes here,
            # OR better: Download the image from the URL and forward it.
            pass 
            
            # Since create_report receives JSON (ReportCreate), it doesn't receive the file directly here.
            # The file upload likely happens in a separate endpoint or handled differently.
            # However, looking at the previous code, there was no file upload logic here.
            # If we want to support this, we need to fetch the image.
            
        except Exception as e:
            print(f"AI Ensemble failed: {e}")

    # For now, let's stick to the previous pattern but add the new service call logic. 
    # Since the new service input requires an IMAGE FILE upload, 
    # but our `create_report` takes a JSON body with `image_url`.
    # We might need to fetch that image or change how create_report works.
    
    # Strategy:
    # 1. If image_url is present, fetch it.
    # 2. Send to ai-ensemble.
    
    visual = 0.0
    depth = 0.0
    urgency = 0.0
    loc_score = 0.0
    final_prio = 0.0
    
    if report.image_url:
        try:
            async with httpx.AsyncClient() as client:
                # 1. Fetch Image
                img_resp = await client.get(report.image_url)
                if img_resp.status_code == 200:
                    image_bytes = img_resp.content
                    
                    # 2. Call AI Service
                    files = {'image': ('report.jpg', image_bytes, 'image/jpeg')}
                    data = {
                        'description': report.description,
                        'lat': str(report.latitude),
                        'lon': str(report.longitude)
                    }
                    
                    ai_resp = await client.post(f"{AI_ENSEMBLE_URL}/analyze", data=data, files=files, timeout=30.0)
                    
                    if ai_resp.status_code == 200:
                        res = ai_resp.json()
                        visual = res['visual_severity_score']
                        depth = res.get('depth_score', 0.0)
                        urgency = res['urgency_score']
                        loc_score = res['location_impact_score']
                        final_prio = res['final_priority_score']
                        ai_details_str = str(res['details'])
                        
                        # Set Priority Enum based on final score
                        if final_prio > 80:
                            priority = ReportPriority.critical
                            severity = ReportSeverity.critical
                        elif final_prio > 50:
                            priority = ReportPriority.high
                            severity = ReportSeverity.high
                        elif final_prio > 30:
                            priority = ReportPriority.medium
                            severity = ReportSeverity.medium
                        else:
                            priority = ReportPriority.low
                            severity = ReportSeverity.low
        except Exception as e:
            print(f"AI Analysis failed: {e}")
            # Fallback to defaults
            severity = ReportSeverity.medium
            priority = ReportPriority.medium

    new_report = Report(
        title=report.title,
        description=report.description,
        category=predicted_category,
        severity=severity,
        priority=priority,
        status=ReportStatus.pending,
        image_url=report.image_url,
        location=WKTElement(location_wkt, srid=4326),
        user_id=current_user.id,
        department_id=department_id,
        visual_score=visual,
        depth_score=depth,
        urgency_score=urgency,
        location_score=loc_score,
        final_priority_score=final_prio,
        ai_details=ai_details_str
    )
    
    # TODO: Trigger AI duplicate check here (async task or direct call)
    # For now, we'll add it as a synchronous call for MVP
    try:
        async with httpx.AsyncClient() as client:
            # Get embedding for the new report
            embed_response = await client.post(
                f"{AI_DUPLICATE_URL}/embed",
                json={"text": f"{report.title}. {report.description}"},
                timeout=10.0
            )
            if embed_response.status_code == 200:
                embedding = embed_response.json()["embedding"]
                new_report.embedding = embedding
    except Exception as e:
        print(f"Embedding generation failed: {e}")
    
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report

@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius: Optional[float] = Query(None, description="Radius in meters"),
    category: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", description="Sort by: created_at, upvotes, priority"),
    sort_order: Optional[str] = Query("desc", description="asc or desc"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Report)
    
    # Category filter
    if category:
        query = query.where(Report.category == category)
    
    # Status filter
    if status:
        try:
            status_enum = ReportStatus[status]
            query = query.where(Report.status == status_enum)
        except KeyError:
            pass
    
    # Priority filter
    if priority:
        try:
            priority_enum = ReportPriority[priority]
            query = query.where(Report.priority == priority_enum)
        except KeyError:
            pass
    
    # Date range filter
    if start_date:
        query = query.where(Report.created_at >= start_date)
    if end_date:
        query = query.where(Report.created_at <= end_date)
        
    # Location-based filter
    if lat is not None and lon is not None and radius is not None:
        pt = WKTElement(f"POINT({lon} {lat})", srid=4326)
        query = query.where(
            func.ST_DWithin(
                Report.location.cast(func.geography),
                func.ST_GeogFromText(f"SRID=4326;POINT({lon} {lat})"),
                radius
            )
        )
    
    # Sorting
    if sort_by == "upvotes":
        order_col = Report.upvotes
    elif sort_by == "priority":
        # Custom ordering for priority enum
        order_col = Report.priority
    else:
        order_col = Report.created_at
    
    if sort_order == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    # Convert geometry to lat/lon
    response_reports = []
    for r in reports:
        if r.location is not None:
            point = to_shape(r.location)
            r.latitude = point.y
            r.longitude = point.x
        else:
            r.latitude = 0.0
            r.longitude = 0.0
        
        response_reports.append(r)

    return response_reports

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.location is not None:
        point = to_shape(report.location)
        report.latitude = point.y
        report.longitude = point.x
    else:
        report.latitude = 0.0
        report.longitude = 0.0
    return report

@router.post("/{report_id}/verify", response_model=ReportResponse)
async def verify_report(
    report_id: int,
    feedback: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Citizen verifies the resolution."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if report.status != ReportStatus.resolved:
        raise HTTPException(status_code=400, detail="Report is not in resolved state")

    report.status = ReportStatus.closed
    report.citizen_feedback = feedback
    await db.commit()
    await db.refresh(report)
    return report

@router.post("/{report_id}/reopen", response_model=ReportResponse)
async def reopen_report(
    report_id: int,
    feedback: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Citizen rejects resolution and reopens report."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    report.status = ReportStatus.reopened
    report.citizen_feedback = feedback
    await db.commit()
    await db.refresh(report)
    return report
