from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.field import Field
from app.models.diagnosis import Diagnosis
from app.models.weather import WeatherData
from app.models.alert import Alert

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farms = (
        db.query(Farm)
        .filter(Farm.user_id == current_user.id)
        .all()
    )

    dashboard_fields = []

    total_fields = 0
    total_diagnoses = 0
    high_risk_fields = 0

    for farm in farms:

        fields = (
            db.query(Field)
            .filter(Field.farm_id == farm.id)
            .all()
        )

        for field in fields:

            total_fields += 1

            diagnosis = (
                db.query(Diagnosis)
                .filter(
                    Diagnosis.field_id == field.id
                )
                .order_by(
                    Diagnosis.created_at.desc()
                )
                .first()
            )

            weather = (
                db.query(WeatherData)
                .filter(
                    WeatherData.field_id == field.id
                )
                .order_by(
                    WeatherData.created_at.desc()
                )
                .first()
            )

            alerts = (
                db.query(Alert)
                .filter(
                    Alert.field_id == field.id,
                    Alert.is_read == False
                )
                .order_by(
                    Alert.created_at.desc()
                )
                .all()
            )

            if diagnosis:
                total_diagnoses += 1

            field_data = {
                "field_id": field.id,
                "field_name": field.name,
                "farm_id": farm.id,
                "farm_name": farm.name,
                "crop": field.crop,
                "variety": field.variety,
                "growth_stage": field.growth_stage,
                "latest_diagnosis": None,
                "weather": None,
                "alerts": []
            }

            if diagnosis:
                field_data["latest_diagnosis"] = {
                    "id": diagnosis.id,
                    "disease": diagnosis.disease,
                    "confidence": diagnosis.confidence,
                    "severity": diagnosis.severity,
                    "affected_area": diagnosis.affected_area,
                    "status": diagnosis.status,
                    "created_at": diagnosis.created_at
                }

            if weather:
                field_data["weather"] = {
                    "temperature": weather.temperature,
                    "humidity": weather.humidity,
                    "rainfall": weather.rainfall,
                    "wind_speed": weather.wind_speed,
                    "forecast_date": weather.forecast_date
                }

            for alert in alerts:
                field_data["alerts"].append({
                    "id": alert.id,
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "created_at": alert.created_at
                })

                if alert.severity == "high":
                    high_risk_fields += 1

            dashboard_fields.append(field_data)

    unread_alerts = (
        db.query(Alert)
        .join(Field)
        .join(Farm)
        .filter(
            Farm.user_id == current_user.id,
            Alert.is_read == False
        )
        .count()
    )

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "language": current_user.language
        },
        "summary": {
            "total_farms": len(farms),
            "total_fields": total_fields,
            "total_diagnoses": total_diagnoses,
            "high_risk_fields": high_risk_fields,
            "unread_alerts": unread_alerts
        },
        "fields": dashboard_fields
    }