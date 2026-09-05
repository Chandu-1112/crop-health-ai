
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, timezone

from app.database.database import get_db
from app.models.field import Field
from app.models.farm import Farm
from app.models.weather import WeatherData
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.weather import get_weather


router = APIRouter(
    prefix="/api/weather",
    tags=["Weather"]
)


@router.get("/field/{field_id}")
def get_field_weather(
    field_id: int,
    refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check that the field belongs to the logged-in user
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

    # Check field location
    if (
        field.farm.latitude is None
        or field.farm.longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Field location is not available"
        )

    recent_weather = (
        db.query(WeatherData)
        .filter(WeatherData.field_id == field.id)
        .order_by(WeatherData.created_at.desc())
        .first()
    )

    # Do not call the provider more than once per 30 minutes for a field.
    recent_cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    if (
        not refresh
        and
        recent_weather is not None
        and recent_weather.created_at is not None
        and recent_weather.created_at >= recent_cutoff
    ):
        weather = {
            "temperature": recent_weather.temperature,
            "humidity": recent_weather.humidity,
            "rainfall": recent_weather.rainfall,
            "wind_speed": recent_weather.wind_speed,
        }
        return {
            "field_id": field.id,
            "field_name": field.name,
            "weather": weather,
            "saved": False,
            "cached": True,
        }

    try:
        weather = get_weather(
            field.farm.latitude,
            field.farm.longitude,
            force_refresh=refresh,
        )
    except Exception:
        if recent_weather is None:
            raise HTTPException(
                status_code=503,
                detail="Weather provider is temporarily unavailable",
            )
        weather = {
            "temperature": recent_weather.temperature,
            "humidity": recent_weather.humidity,
            "rainfall": recent_weather.rainfall,
            "wind_speed": recent_weather.wind_speed,
        }
        return {
            "field_id": field.id,
            "field_name": field.name,
            "weather": weather,
            "saved": False,
            "cached": True,
        }

    # Save weather in database
    weather_data = WeatherData(
        field_id=field.id,
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        rainfall=weather["rainfall"],
        wind_speed=weather["wind_speed"],
        forecast_date=date.today()
    )

    db.add(weather_data)
    db.commit()
    db.refresh(weather_data)

    return {
        "field_id": field.id,
        "field_name": field.name,
        "weather": weather,
        "saved": True
    }
