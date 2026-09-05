from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.expert_review import ExpertReview
from app.models.diagnosis import Diagnosis
from app.models.field import Field
from app.models.farm import Farm
from app.models.user import User

from app.schemas.expert_review import (
    ExpertReviewCreate,
    ExpertReviewUpdate,
    ExpertReviewResponse
)

from app.core.dependencies import get_current_user


def require_expert(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {"expert", "extension_officer", "admin"}:
        raise HTTPException(status_code=403, detail="Expert access required")
    return current_user


router = APIRouter(
    prefix="/api/expert-reviews",
    tags=["Expert Reviews"]
)


@router.post(
    "/diagnosis/{diagnosis_id}",
    response_model=ExpertReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def request_expert_review(
    diagnosis_id: int,
    review_data: ExpertReviewCreate,
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

    existing_review = (
        db.query(ExpertReview)
        .filter(
            ExpertReview.diagnosis_id == diagnosis_id,
            ExpertReview.status == "pending"
        )
        .first()
    )

    if existing_review:
        return existing_review

    review = ExpertReview(
        diagnosis_id=diagnosis_id,
        status="pending",
        expert_notes=review_data.notes
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get(
    "/diagnosis/{diagnosis_id}",
    response_model=List[ExpertReviewResponse]
)
def get_diagnosis_reviews(
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

    reviews = (
        db.query(ExpertReview)
        .filter(
            ExpertReview.diagnosis_id == diagnosis_id
        )
        .order_by(
            ExpertReview.created_at.desc()
        )
        .all()
    )

    return reviews


@router.get("/queue", response_model=List[ExpertReviewResponse])
def get_expert_queue(
    _expert: User = Depends(require_expert),
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(ExpertReview, User.name, Field.crop)
        .join(Diagnosis, ExpertReview.diagnosis_id == Diagnosis.id)
        .join(Field, Diagnosis.field_id == Field.id)
        .join(Farm, Field.farm_id == Farm.id)
        .join(User, Farm.user_id == User.id)
        .filter(ExpertReview.status == "pending")
        .order_by(ExpertReview.created_at.asc())
        .all()
    )
    result = []
    for review, farmer_name, crop in reviews:
        result.append({
            "id": review.id,
            "diagnosis_id": review.diagnosis_id,
            "status": review.status,
            "expert_diagnosis": review.expert_diagnosis,
            "expert_notes": review.expert_notes,
            "created_at": review.created_at,
            "farmer_name": farmer_name,
            "crop": crop,
            "diagnosis": {
                "disease": review.diagnosis.disease,
                "confidence": review.diagnosis.confidence,
                "severity": review.diagnosis.severity,
                "explanation": review.diagnosis.explanation,
            },
        })
    return result


@router.get(
    "/{review_id}",
    response_model=ExpertReviewResponse
)
def get_expert_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = (
        db.query(ExpertReview)
        .join(Diagnosis)
        .join(Field)
        .join(Farm)
        .filter(
            ExpertReview.id == review_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert review not found"
        )

    return review


@router.put(
    "/{review_id}",
    response_model=ExpertReviewResponse
)
def update_expert_review(
    review_id: int,
    review_data: ExpertReviewUpdate,
    current_user: User = Depends(require_expert),
    db: Session = Depends(get_db)
):
    review = (
        db.query(ExpertReview)
        .join(Diagnosis)
        .join(Field)
        .join(Farm)
        .filter(
            ExpertReview.id == review_id,
            Farm.user_id == current_user.id
        )
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert review not found"
        )

    review.status = review_data.status

    if review_data.expert_diagnosis is not None:
        review.expert_diagnosis = review_data.expert_diagnosis

    if review_data.expert_notes is not None:
        review.expert_notes = review_data.expert_notes

    db.commit()
    db.refresh(review)

    return review