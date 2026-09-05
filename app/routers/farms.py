from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.models.weather import WeatherData
from app.models.alert import Alert
from app.models.diagnosis import Diagnosis
from app.models.treatment import Treatment
from app.models.monitoring import Monitoring
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/farms",
    tags=["Farms"]
)


# Create a new farm
@router.post(
    "",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED
)
def create_farm(
    farm_data: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = Farm(
        user_id=current_user.id,
        name=farm_data.name,
        area=farm_data.area,
        latitude=farm_data.latitude,
        longitude=farm_data.longitude
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farm


# Get all farms of the logged-in user
@router.get(
    "",
    response_model=List[FarmResponse]
)
def get_my_farms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farms = (
        db.query(Farm)
        .filter(Farm.user_id == current_user.id)
        .all()
    )

    return farms


# Get a specific farm
@router.get(
    "/{farm_id}",
    response_model=FarmResponse
)
def get_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    farm = (
        db.query(Farm)
        .filter(
            Farm.id == farm_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )

    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = (
        db.query(Farm)
        .filter(Farm.id == farm_id, Farm.user_id == current_user.id)
        .first()
    )
    if farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    field_ids = [field.id for field in db.query(Field.id).filter(Field.farm_id == farm_id).all()]
    diagnosis_ids = [
        diagnosis.id
        for diagnosis in db.query(Diagnosis.id).filter(Diagnosis.field_id.in_(field_ids)).all()
    ] if field_ids else []

    if diagnosis_ids:
        db.query(Treatment).filter(Treatment.diagnosis_id.in_(diagnosis_ids)).delete(synchronize_session=False)
        db.query(Monitoring).filter(Monitoring.diagnosis_id.in_(diagnosis_ids)).delete(synchronize_session=False)
        db.query(Diagnosis).filter(Diagnosis.id.in_(diagnosis_ids)).delete(synchronize_session=False)
    if field_ids:
        db.query(WeatherData).filter(WeatherData.field_id.in_(field_ids)).delete(synchronize_session=False)
        db.query(Alert).filter(Alert.field_id.in_(field_ids)).delete(synchronize_session=False)
        db.query(Field).filter(Field.id.in_(field_ids)).delete(synchronize_session=False)

    db.delete(farm)
    db.commit()
    return None