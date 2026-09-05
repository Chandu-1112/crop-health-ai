from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, LanguageUpdate
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


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