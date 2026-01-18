from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Vote, Report, User
from routers.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["votes"])

@router.post("/{report_id}/upvote")
async def upvote_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upvote a report. Creates or updates vote."""
    # Check if report exists
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user already voted
    vote_result = await db.execute(
        select(Vote).where(
            Vote.user_id == current_user.id,
            Vote.report_id == report_id
        )
    )
    existing_vote = vote_result.scalars().first()
    
    if existing_vote:
        if existing_vote.value == 1:
            # Already upvoted, remove vote
            await db.delete(existing_vote)
            report.upvotes = max(0, report.upvotes - 1)
        else:
            # Was downvote, change to upvote
            existing_vote.value = 1
            report.upvotes += 1
    else:
        # New upvote
        new_vote = Vote(user_id=current_user.id, report_id=report_id, value=1)
        db.add(new_vote)
        report.upvotes += 1
    
    await db.commit()
    await db.refresh(report)

    # --- DYNAMIC RE-EVALUATION ---
    await recalculate_ai_score(report, db)
    
    return {"message": "Vote recorded", "upvotes": report.upvotes}

@router.post("/{report_id}/downvote")
async def downvote_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Downvote a report. Creates or updates vote."""
    # Check if report exists
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user already voted
    vote_result = await db.execute(
        select(Vote).where(
            Vote.user_id == current_user.id,
            Vote.report_id == report_id
        )
    )
    existing_vote = vote_result.scalars().first()
    
    if existing_vote:
        if existing_vote.value == -1:
            # Already downvoted, remove vote
            await db.delete(existing_vote)
        else:
            # Was upvote, change to downvote
            existing_vote.value = -1
            report.upvotes = max(0, report.upvotes - 1)
    else:
        # New downvote (doesn't affect upvote count)
        new_vote = Vote(user_id=current_user.id, report_id=report_id, value=-1)
        db.add(new_vote)
    
    await db.commit()
    await db.refresh(report)

    # --- DYNAMIC RE-EVALUATION ---
    await recalculate_ai_score(report, db)
    
    return {"message": "Vote recorded", "upvotes": report.upvotes}


import httpx
import os
import json
import logging

# Re-calc Function
async def recalculate_ai_score(report: Report, db: AsyncSession):
    """
    Recalculate AI Severity when Social Score (Upvotes) changes.
    Only allows this for Hybrid Reports (waste_management) for now.
    """
    try:
        if report.category != "waste_management" or not report.sentiment_meta:
            return

        # Parse stored metadata to get original 7 features
        try:
            meta = json.loads(report.sentiment_meta) if isinstance(report.sentiment_meta, str) else report.sentiment_meta
            if not meta or "features" not in meta:
                return # Old report format
            
            features = meta["features"]
        except:
            return

        # Update Social Score
        new_social_score = min(report.upvotes / 50.0, 1.0)
        features["social_score"] = new_social_score
        
        # Call Parent Model
        GARBAGE_PARENT_URL = os.getenv("AI_GARBAGE_PARENT_URL", "http://ai-garbage-parent:8004")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{GARBAGE_PARENT_URL}/predict", json=features, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                new_score = data['severity_score']
                new_level = data['severity_level']
                
                # Update DB
                report.ai_severity_score = new_score
                report.ai_severity_level = new_level
                
                # Update Features in Meta too (so future votes use new social score base)
                meta["features"]["social_score"] = new_social_score
                meta["full_21_features"]["social_urgency"] = new_social_score # Sync display data
                report.sentiment_meta = json.dumps(meta)
                
                await db.commit()
                print(f"Dynamic Score Update: Report {report.id} -> {new_score} ({new_level})")

    except Exception as e:
        print(f"Failed to recalculate score: {e}")
