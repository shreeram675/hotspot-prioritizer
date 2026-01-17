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
    
    
    # Domain-specific AI Analysis
    ai_scores = {}
    severity = ReportSeverity.medium  # Default
    priority = ReportPriority.medium
    
    if report.image_url and predicted_category in ["pothole", "garbage"]:
        try:
            if predicted_category == "pothole":
                from ai_analysis import analyze_pothole_report
                ai_scores = await analyze_pothole_report(
                    image_url=report.image_url,
                    description=report.description,
                    latitude=report.latitude,
                    longitude=report.longitude,
                    upvotes=0
                )
            elif predicted_category == "garbage":
                from ai_analysis import analyze_garbage_report
                ai_scores = await analyze_garbage_report(
                    image_url=report.image_url,
                    description=report.description,
                    latitude=report.latitude,
                    longitude=report.longitude,
                    upvotes=0
                )
            
            # Map AI severity score to enum
            ai_severity = ai_scores.get('ai_severity_score', 50.0)
            if ai_severity > 75:
                severity = ReportSeverity.critical
                priority = ReportPriority.critical
            elif ai_severity > 50:
                severity = ReportSeverity.high
                priority = ReportPriority.high
            elif ai_severity > 25:
                severity = ReportSeverity.medium
                priority = ReportPriority.medium
            else:
                severity = ReportSeverity.low
                priority = ReportPriority.low
                
        except Exception as e:
            print(f"AI Analysis failed: {e}")
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
        # AI Scores
        pothole_depth_score=ai_scores.get('pothole_depth_score'),
        pothole_spread_score=ai_scores.get('pothole_spread_score'),
        garbage_volume_score=ai_scores.get('garbage_volume_score'),
        garbage_waste_type_score=ai_scores.get('garbage_waste_type_score'),
        emotion_score=ai_scores.get('emotion_score'),
        location_score=ai_scores.get('location_score'),
        upvote_score=ai_scores.get('upvote_score'),
        ai_severity_score=ai_scores.get('ai_severity_score'),
        ai_severity_level=ai_scores.get('ai_severity_level')
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
        order_col = Report.priority
    elif sort_by == "ai_severity_score":
        order_col = Report.ai_severity_score
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
