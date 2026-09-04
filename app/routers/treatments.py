from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.treatment import Treatment
from app.models.diagnosis import Diagnosis
from app.models.field import Field
from app.models.farm import Farm
from app.models.monitoring import Monitoring
from app.models.user import User

from app.schemas.treatment import (
    TreatmentCreate,
    TreatmentUpdate,
    TreatmentResponse
)

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/treatments",
    tags=["Treatments"]
)


@router.post(
    "/diagnosis/{diagnosis_id}",
    response_model=TreatmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_treatment(
    diagnosis_id: int,
    treatment_data: TreatmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diagnosis = (
        db.query(Diagnosis)
        .join(Field)
        .join(Farm)
        .filter(
            Diagnosis.id == diagnosis_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if diagnosis is None:
        raise HTTPException(
            status_code=404,
            detail="Diagnosis not found"
        )

    treatment = Treatment(
        diagnosis_id=diagnosis_id,
        recommendation=treatment_data.recommendation,
        treatment_type=treatment_data.treatment_type,
        started_at=treatment_data.started_at
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    return treatment


@router.get(
    "/diagnosis/{diagnosis_id}",
    response_model=List[TreatmentResponse]
)
def get_diagnosis_treatments(
    diagnosis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diagnosis = (
        db.query(Diagnosis)
        .join(Field)
        .join(Farm)
        .filter(
            Diagnosis.id == diagnosis_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if diagnosis is None:
        raise HTTPException(
            status_code=404,
            detail="Diagnosis not found"
        )

    treatments = (
        db.query(Treatment)
        .filter(
            Treatment.diagnosis_id == diagnosis_id
        )
        .order_by(
            Treatment.created_at.desc()
        )
        .all()
    )

    return treatments


@router.put(
    "/{treatment_id}",
    response_model=TreatmentResponse
)
def update_treatment(
    treatment_id: int,
    treatment_data: TreatmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    treatment = (
        db.query(Treatment)
        .join(Diagnosis)
        .join(Field)
        .join(Farm)
        .filter(
            Treatment.id == treatment_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if treatment is None:
        raise HTTPException(
            status_code=404,
            detail="Treatment not found"
        )

    if treatment_data.result is not None:
        treatment.result = treatment_data.result

    if treatment_data.started_at is not None:
        treatment.started_at = treatment_data.started_at

    db.commit()
    db.refresh(treatment)

    return treatment


@router.get(
    "/{treatment_id}/effectiveness"
)
@router.get(
    "/{treatment_id}/effectiveness"
)
def get_treatment_effectiveness(
    treatment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Find treatment and verify ownership
    treatment = (
        db.query(Treatment)
        .join(Diagnosis)
        .join(Field)
        .join(Farm)
        .filter(
            Treatment.id == treatment_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if treatment is None:
        raise HTTPException(
            status_code=404,
            detail="Treatment not found"
        )

    # 2. Get all monitoring records
    monitoring_records = (
        db.query(Monitoring)
        .filter(
            Monitoring.diagnosis_id == treatment.diagnosis_id
        )
        .order_by(
            Monitoring.created_at.asc()
        )
        .all()
    )

    # 3. No follow-up yet
    if not monitoring_records:
        return {
            "treatment_id": treatment.id,
            "treatment_type": treatment.treatment_type,
            "recorded_result": treatment.result,
            "status": "no_follow_up",
            "effectiveness": "unknown",
            "monitoring_count": 0,
            "message": (
                "No follow-up monitoring record "
                "available yet."
            )
        }

    # 4. Count monitoring outcomes
    improved_count = 0
    worsened_count = 0
    same_count = 0

    for record in monitoring_records:

        if record.comparison == "improved":
            improved_count += 1

        elif record.comparison == "worsened":
            worsened_count += 1

        elif record.comparison == "same":
            same_count += 1

    # 5. Determine overall effectiveness
    total = len(monitoring_records)

    if improved_count > worsened_count:
        effectiveness = "effective"

    elif worsened_count > improved_count:
        effectiveness = "not_effective"

    elif improved_count > 0 and improved_count == worsened_count:
        effectiveness = "partially_effective"

    else:
        effectiveness = "partially_effective"

    # 6. Get latest monitoring record
    latest_monitoring = monitoring_records[-1]

    return {
        "treatment_id": treatment.id,
        "treatment_type": treatment.treatment_type,
        "recorded_result": treatment.result,

        "effectiveness": effectiveness,

        "monitoring_summary": {
            "total_records": total,
            "improved": improved_count,
            "same": same_count,
            "worsened": worsened_count
        },

        "latest_monitoring": {
            "id": latest_monitoring.id,
            "disease": latest_monitoring.disease,
            "severity": latest_monitoring.severity,
            "affected_area": latest_monitoring.affected_area,
            "comparison": latest_monitoring.comparison,
            "created_at": latest_monitoring.created_at
        }
    }


@router.delete(
    "/{treatment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_treatment(
    treatment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    treatment = (
        db.query(Treatment)
        .join(Diagnosis)
        .join(Field)
        .join(Farm)
        .filter(
            Treatment.id == treatment_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if treatment is None:
        raise HTTPException(
            status_code=404,
            detail="Treatment not found"
        )

    db.delete(treatment)
    db.commit()

    return None