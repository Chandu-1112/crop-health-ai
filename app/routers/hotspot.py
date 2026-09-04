from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.hotspot import detect_hotspots


router = APIRouter(
    prefix="/api/hotspots",
    tags=["Hotspots"]
)


@router.get("")
def get_hotspots(
    disease: str = Query(..., min_length=2),
    minimum_cases: int = Query(
        default=3,
        ge=2
    ),
    days: int = Query(
        default=14,
        ge=1,
        le=90
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    hotspots = detect_hotspots(
        db=db,
        disease=disease,
        minimum_cases=minimum_cases,
        days=days
    )

    return {
        "disease": disease,
        "minimum_cases": minimum_cases,
        "time_window_days": days,
        "hotspot_count": len(hotspots),
        "hotspots": hotspots
    }