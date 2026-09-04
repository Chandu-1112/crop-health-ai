from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.alert import Alert
from app.models.field import Field
from app.models.farm import Farm
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.alert import AlertResponse


router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"]
)


# -----------------------------------------
# Get all alerts for logged-in farmer
# -----------------------------------------

@router.get(
    "",
    response_model=List[AlertResponse]
)
def get_my_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    alerts = (
        db.query(Alert)
        .join(Field)
        .join(Farm)
        .filter(
            Farm.user_id == current_user.id
        )
        .order_by(
            Alert.created_at.desc()
        )
        .all()
    )

    return alerts


# -----------------------------------------
# Get alerts for a specific field
# -----------------------------------------

@router.get(
    "/field/{field_id}",
    response_model=List[AlertResponse]
)
def get_field_alerts(
    field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

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

    alerts = (
        db.query(Alert)
        .filter(
            Alert.field_id == field_id
        )
        .order_by(
            Alert.created_at.desc()
        )
        .all()
    )

    return alerts


# -----------------------------------------
# Mark alert as read
# -----------------------------------------

@router.put(
    "/{alert_id}/read"
)
def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .join(Field)
        .join(Farm)
        .filter(
            Alert.id == alert_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    alert.is_read = True

    db.commit()
    db.refresh(alert)

    return {
        "message": "Alert marked as read",
        "alert_id": alert.id
    }