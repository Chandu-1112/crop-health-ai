from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File
)
from typing import List
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.monitoring import Monitoring
from app.models.diagnosis import Diagnosis
from app.models.field import Field
from app.models.farm import Farm
from app.models.user import User

from app.schemas.monitoring import MonitoringResponse

from app.core.dependencies import get_current_user
from app.services.storage import save_image
from app.services.disease import analyze_crop_image


router = APIRouter(
    prefix="/api/monitoring",
    tags=["Monitoring"]
)


def compare_condition(
    old_severity: str,
    new_severity: str,
    old_area: float,
    new_area: float
):
    severity_order = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    old_level = severity_order.get(
        old_severity.lower(),
        2
    )

    new_level = severity_order.get(
        new_severity.lower(),
        2
    )

    if (
        new_area < old_area
        or new_level < old_level
    ):
        return "improved"

    if (
        new_area > old_area
        or new_level > old_level
    ):
        return "worsened"

    return "same"


@router.post(
    "/diagnosis/{diagnosis_id}",
    response_model=MonitoringResponse,
    status_code=status.HTTP_201_CREATED
)
def create_monitoring_record(
    diagnosis_id: int,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Verify diagnosis belongs to current user
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )

    # 2. Validate image
    if (
        not image.content_type
        or not image.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a valid image"
        )

    image_bytes = image.file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty"
        )

    # 3. Save image
    image_url = save_image(image)

    # 4. Analyze follow-up image
    try:
        ai_result = analyze_crop_image(
            image_bytes=image_bytes,
            crop=diagnosis.field.crop,
            mime_type=image.content_type,
            language=current_user.language
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI monitoring analysis failed: {str(e)}"
        )

    new_disease = ai_result.get(
        "disease",
        "Unable to determine"
    )

    new_confidence = ai_result.get(
        "confidence",
        0.0
    )

    new_severity = ai_result.get(
        "severity",
        "unknown"
    )

    new_area = ai_result.get(
        "affected_area",
        0.0
    )

    # 5. Find previous monitoring record
    previous_monitoring = (
        db.query(Monitoring)
        .filter(
            Monitoring.diagnosis_id == diagnosis_id
        )
        .order_by(
            Monitoring.created_at.desc()
        )
        .first()
    )

    # 6. Determine comparison baseline
    if previous_monitoring:

        old_severity = (
            previous_monitoring.severity
            or "unknown"
        )

        old_area = (
            previous_monitoring.affected_area
            or 0.0
        )

    else:

        old_severity = (
            diagnosis.severity
            or "unknown"
        )

        old_area = (
            diagnosis.affected_area
            or 0.0
        )

    # 7. Compare new condition with previous condition
    if new_severity != "unknown":

        comparison = compare_condition(
            old_severity=old_severity,
            new_severity=new_severity,
            old_area=old_area,
            new_area=new_area
        )

    else:
        comparison = "same"

    # 8. Save monitoring record
    monitoring = Monitoring(
        diagnosis_id=diagnosis_id,
        image_url=image_url,
        disease=new_disease,
        confidence=new_confidence,
        severity=new_severity,
        affected_area=new_area,
        comparison=comparison,
        notes=ai_result.get(
            "explanation",
            ""
        )
    )

    db.add(monitoring)
    db.commit()
    db.refresh(monitoring)

    return monitoring


@router.get(
    "/diagnosis/{diagnosis_id}",
    response_model=List[MonitoringResponse]
)
def get_monitoring_history(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )

    records = (
        db.query(Monitoring)
        .filter(
            Monitoring.diagnosis_id == diagnosis_id
        )
        .order_by(
            Monitoring.created_at.desc()
        )
        .all()
    )

    return records