# backend/routers/scan_router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from auth import get_optional_user, get_current_user
import db_models
from models import ScanRequest, ScanResult, ScanHistoryItem, ScanHistoryResponse
from analyzer import analyze_message
from typing import Optional
 
router = APIRouter(tags=["Scans"])
 
 
@router.post("/scan", response_model=ScanResult)
async def scan(
    body: ScanRequest,
    db: Session = Depends(get_db),
    current_user: Optional[db_models.User] = Depends(get_optional_user),
):
    try:
        result = await analyze_message(body.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
 
    # Save scan to DB — user_id is None for anonymous scans
    scan_record = db_models.Scan(
        user_id=current_user.id if current_user else None,
        message=body.message,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        summary=result.summary,
        reasons=result.reasons,
        action=result.action,
        what_to_do=result.what_to_do,
        pass1_blocked=result.pass1_blocked,
    )
    db.add(scan_record)
    db.commit()
 
    return result
 
 
@router.get("/scans/history", response_model=ScanHistoryResponse)
def get_history(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    #current_user: db_models.User = Depends(get_current_user),  # must be logged in
    current_user: Optional[db_models.User] = Depends(get_optional_user),
):
    query = db.query(db_models.Scan)
 
    if user_id:
        query = query.filter(db_models.Scan.user_id == user_id)
 
    total = query.count()
    scans = (
        query.order_by(db_models.Scan.scanned_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
 
    return ScanHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        scans=[
            ScanHistoryItem(
                id=s.id,
                user_id=s.user_id,
                message=s.message,
                risk_score=s.risk_score,
                risk_level=s.risk_level,
                summary=s.summary,
                reasons=s.reasons,
                action=s.action,
                what_to_do=s.what_to_do,
                pass1_blocked=s.pass1_blocked,
                scanned_at=s.scanned_at,
            )
            for s in scans
        ],
    )