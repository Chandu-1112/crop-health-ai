from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.field import Field
from app.models.diagnosis import Diagnosis
from app.models.weather import WeatherData
from app.models.alert import Alert
from app.models.treatment import Treatment
from app.models.monitoring import Monitoring
from app.models.farm import Farm
from app.models.user import User
from app.schemas.field import FieldCreate, FieldResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/farms/{farm_id}/fields",
    tags=["Fields"]
)


# Create a new field
@router.post(
    "",
    response_model=FieldResponse,
    status_code=status.HTTP_201_CREATED
)
def create_field(
    farm_id: int,
    field_data: FieldCreate,
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

    field = Field(
        farm_id=farm_id,
        name=field_data.name,
        crop=field_data.crop,
        variety=field_data.variety,
        growth_stage=field_data.growth_stage,
        planting_date=field_data.planting_date,
        area=field_data.area
    )

    db.add(field)
    db.commit()
    db.refresh(field)

    return field


# Get all fields inside a farm
@router.get(
    "",
    response_model=List[FieldResponse]
)
def get_fields(
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

    fields = (
        db.query(Field)
        .filter(Field.farm_id == farm_id)
        .all()
    )

    return fields


# Get a specific field
@router.get(
    "/{field_id}",
    response_model=FieldResponse
)
def get_field(
    farm_id: int,
    field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    field = (
        db.query(Field)
        .join(Farm)
        .filter(
            Field.id == field_id,
            Field.farm_id == farm_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if field is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )

    return field


# Update a field
@router.put(
    "/{field_id}",
    response_model=FieldResponse
)
def update_field(
    farm_id: int,
    field_id: int,
    field_data: FieldCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    field = (
        db.query(Field)
        .join(Farm)
        .filter(
            Field.id == field_id,
            Field.farm_id == farm_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if field is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )

    field.name = field_data.name
    field.crop = field_data.crop
    field.variety = field_data.variety
    field.growth_stage = field_data.growth_stage
    field.planting_date = field_data.planting_date
    field.area = field_data.area

    db.commit()
    db.refresh(field)

    return field


# Delete a field
@router.delete(
    "/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_field(
    farm_id: int,
    field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    field = (
        db.query(Field)
        .join(Farm)
        .filter(
            Field.id == field_id,
            Field.farm_id == farm_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if field is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )

    diagnosis_ids = [
        diagnosis.id
        for diagnosis in db.query(Diagnosis.id).filter(Diagnosis.field_id == field_id).all()
    ]
    if diagnosis_ids:
        db.query(Treatment).filter(Treatment.diagnosis_id.in_(diagnosis_ids)).delete(synchronize_session=False)
        db.query(Monitoring).filter(Monitoring.diagnosis_id.in_(diagnosis_ids)).delete(synchronize_session=False)
        db.query(Diagnosis).filter(Diagnosis.id.in_(diagnosis_ids)).delete(synchronize_session=False)
    db.query(WeatherData).filter(WeatherData.field_id == field_id).delete(synchronize_session=False)
    db.query(Alert).filter(Alert.field_id == field_id).delete(synchronize_session=False)
    db.delete(field)
    db.commit()

    return None