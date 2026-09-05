from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.field import Field
from app.models.farm import Farm
from app.models.diagnosis import Diagnosis
from app.models.weather import WeatherData
from app.models.user import User

from app.core.dependencies import get_current_user

from app.services.risk_engine import calculate_risk
from app.services.recommendation import generate_recommendations
from app.services.alert_service import create_risk_alert


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


@router.get("/field/{field_id}", response_model=Dict[str, Any])
def get_recommendations(
    field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # Check field ownership
    # -----------------------------------------

    field = (
        db.query(Field)
        .join(Farm)
        .filter(
            Field.id == field_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    # -----------------------------------------
    # Get latest diagnosis
    # -----------------------------------------

    diagnosis = (
        db.query(Diagnosis)
        .filter(
            Diagnosis.field_id == field_id
        )
        .order_by(
            Diagnosis.created_at.desc()
        )
        .first()
    )

    if diagnosis is None:
        raise HTTPException(
            status_code=404,
            detail="No diagnosis found for this field"
        )

    # -----------------------------------------
    # Get latest weather
    # -----------------------------------------

    weather = (
        db.query(WeatherData)
        .filter(
            WeatherData.field_id == field_id
        )
        .order_by(
            WeatherData.created_at.desc()
        )
        .first()
    )

    # Recommendations must remain available even before weather is saved.
    if weather is None:
        severity = (diagnosis.severity or "unknown").lower()
        fallback_level = "high" if severity in {"high", "severe"} else "medium"
        risk = {"risk_level": fallback_level, "risk_score": 0}
    else:
        risk = calculate_risk(
            disease=diagnosis.disease,
            confidence=diagnosis.confidence or 0.0,
            severity=diagnosis.severity or "unknown",
            temperature=weather.temperature,
            humidity=weather.humidity,
            rainfall=weather.rainfall,
            growth_stage=field.growth_stage
        )

    # -----------------------------------------
    # Create alert if required
    # -----------------------------------------

    alert = None
    if weather is not None:
        alert = create_risk_alert(
            db=db,
            field_id=field.id,
            crop=field.crop,
            disease=diagnosis.disease,
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
            language=current_user.language,
        )

    # -----------------------------------------
    # Generate recommendations
    # -----------------------------------------

    recommendations = generate_recommendations(
        disease=diagnosis.disease,
        severity=diagnosis.severity or "unknown",
        risk_level=risk["risk_level"],
        crop=field.crop,
        language=current_user.language,
    )

    # -----------------------------------------
    # Response
    # -----------------------------------------

    return {
        "field_id": field.id,
        "field_name": field.name,
        "crop": field.crop,

        "diagnosis": {
            "disease": diagnosis.disease,
            "confidence": diagnosis.confidence,
            "severity": diagnosis.severity
        },

        "risk": risk,

        "alert": {
            "id": alert.id,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message
        } if alert else None,

        "recommendations": recommendations
    }