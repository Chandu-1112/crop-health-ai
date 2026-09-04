from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.field import Field
from app.models.farm import Farm
from app.models.diagnosis import Diagnosis
from app.models.weather import WeatherData
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.risk_engine import calculate_risk


router = APIRouter(
    prefix="/api/risk",
    tags=["Risk"]
)


@router.get("/field/{field_id}")
def get_field_risk(
    field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check field ownership
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

    # Get latest diagnosis
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

    # Get latest weather
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

    if weather is None:
        raise HTTPException(
            status_code=404,
            detail="No weather data found for this field"
        )

    # Calculate risk
    risk = calculate_risk(
        disease=diagnosis.disease,
        confidence=diagnosis.confidence or 0.0,
        severity=diagnosis.severity or "unknown",
        temperature=weather.temperature,
        humidity=weather.humidity,
        rainfall=weather.rainfall,
        growth_stage=field.growth_stage
    )

    return {
        "field_id": field.id,
        "field_name": field.name,
        "crop": field.crop,
        "growth_stage": field.growth_stage,

        "diagnosis": {
            "disease": diagnosis.disease,
            "confidence": diagnosis.confidence,
            "severity": diagnosis.severity
        },

        "weather": {
            "temperature": weather.temperature,
            "humidity": weather.humidity,
            "rainfall": weather.rainfall,
            "wind_speed": weather.wind_speed
        },

        "risk": risk
    }