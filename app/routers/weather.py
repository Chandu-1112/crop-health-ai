from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

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

```
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

# ---------------------------------------------------------
# Try to get fresh weather from Open-Meteo
# ---------------------------------------------------------
try:
    weather = get_weather(
        field.farm.latitude,
        field.farm.longitude
    )

    # Save fresh weather in database
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
        "saved": True,
        "source": "open-meteo"
    }

# ---------------------------------------------------------
# Open-Meteo unavailable / rate limited
# ---------------------------------------------------------
except Exception as error:
    print(
        f"Weather API failed for field {field.id}: {error}"
    )

    # Get the latest weather already stored in PostgreSQL
    latest_weather = (
        db.query(WeatherData)
        .filter(
            WeatherData.field_id == field.id
        )
        .order_by(
            WeatherData.created_at.desc()
        )
        .first()
    )

    # If previous weather exists, use it
    if latest_weather is not None:
        return {
            "field_id": field.id,
            "field_name": field.name,
            "weather": {
                "temperature": latest_weather.temperature,
                "humidity": latest_weather.humidity,
                "rainfall": latest_weather.rainfall,
                "wind_speed": latest_weather.wind_speed,
                "weather_code": None,
                "time": None,
                "timezone": None
            },
            "saved": False,
            "source": "database-cache",
            "warning": (
                "Live weather is temporarily unavailable. "
                "Showing the latest saved weather data."
            )
        }

    # No live weather and no previous weather
    raise HTTPException(
        status_code=503,
        detail=(
            "Live weather is temporarily unavailable "
            "and no previous weather data is available."
        )
    )

