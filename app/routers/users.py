from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, LanguageUpdate
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "mobile": current_user.mobile,
        "language": current_user.language,
        "role": current_user.role,
        "created_at": current_user.created_at
    }


@router.get("/admin")
def get_all_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    users = db.query(User).order_by(User.id.asc()).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "language": user.language,
            "role": user.role,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin account cannot be deleted"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        # Remove dependent records first because the existing database schema
        # does not declare cascading foreign keys.
        db.execute(
            text(
                """
                DELETE FROM monitoring
                WHERE diagnosis_id IN (
                    SELECT d.id
                    FROM diagnoses d
                    JOIN fields f ON f.id = d.field_id
                    JOIN farms fa ON fa.id = f.farm_id
                    WHERE fa.user_id = :user_id
                )
                """
            ),
            {"user_id": user_id},
        )
        db.execute(
            text(
                """
                DELETE FROM treatments
                WHERE diagnosis_id IN (
                    SELECT d.id
                    FROM diagnoses d
                    JOIN fields f ON f.id = d.field_id
                    JOIN farms fa ON fa.id = f.farm_id
                    WHERE fa.user_id = :user_id
                )
                """
            ),
            {"user_id": user_id},
        )
        db.execute(
            text(
                """
                DELETE FROM diagnoses
                WHERE field_id IN (
                    SELECT f.id
                    FROM fields f
                    JOIN farms fa ON fa.id = f.farm_id
                    WHERE fa.user_id = :user_id
                )
                """
            ),
            {"user_id": user_id},
        )
        db.execute(
            text(
                """
                DELETE FROM weather_data
                WHERE field_id IN (
                    SELECT f.id
                    FROM fields f
                    JOIN farms fa ON fa.id = f.farm_id
                    WHERE fa.user_id = :user_id
                )
                """
            ),
            {"user_id": user_id},
        )
        db.execute(
            text(
                """
                DELETE FROM alerts
                WHERE field_id IN (
                    SELECT f.id
                    FROM fields f
                    JOIN farms fa ON fa.id = f.farm_id
                    WHERE fa.user_id = :user_id
                )
                """
            ),
            {"user_id": user_id},
        )
        db.execute(
            text(
                """
                DELETE FROM fields
                WHERE farm_id IN (
                    SELECT id FROM farms WHERE user_id = :user_id
                )
                """
            ),
            {"user_id": user_id},
        )
        db.execute(
            text("DELETE FROM farms WHERE user_id = :user_id"),
            {"user_id": user_id},
        )
        db.delete(user)
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete user and related records",
        ) from error

    return None


@router.put("/me")
def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.name = user_data.name
    current_user.language = user_data.language

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "mobile": current_user.mobile,
            "language": current_user.language,
            "role": current_user.role
        }
    }


@router.put("/me/language")
def update_language(
    language_data: LanguageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.language = language_data.language

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Language updated successfully",
        "language": current_user.language
    }