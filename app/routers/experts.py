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

    review.status = review_data.status

    if review_data.expert_diagnosis is not None:
        review.expert_diagnosis = review_data.expert_diagnosis

    if review_data.expert_notes is not None:
        review.expert_notes = review_data.expert_notes

    db.commit()
    db.refresh(review)

    return review