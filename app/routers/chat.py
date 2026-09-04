from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.field import Field as FieldModel
from app.models.farm import Farm
from app.models.diagnosis import Diagnosis

from app.services.chat import ask_farmer_question


router = APIRouter(
    prefix="/api/chat",
    tags=["Farmer Chat"]
)


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=1000
    )

    field_id: int | None = None


@router.post("")
def farmer_chat(
    chat_data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crop = None
    disease = None

    # If farmer selected a field,
    # get its crop and latest diagnosis.
    if chat_data.field_id is not None:

        field = (
            db.query(FieldModel)
            .join(Farm)
            .filter(
                FieldModel.id == chat_data.field_id,
                Farm.user_id == current_user.id
            )
            .first()
        )

        if field is None:
            raise HTTPException(
                status_code=404,
                detail="Field not found"
            )

        crop = field.crop

        latest_diagnosis = (
            db.query(Diagnosis)
            .filter(
                Diagnosis.field_id == field.id
            )
            .order_by(
                Diagnosis.created_at.desc()
            )
            .first()
        )

        if latest_diagnosis:
            disease = latest_diagnosis.disease

    try:
        answer = ask_farmer_question(
            question=chat_data.question,
            language=current_user.language,
            crop=crop,
            disease=disease
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI chat failed: {str(e)}"
        )

    return {
        "question": chat_data.question,
        "language": current_user.language,
        "crop": crop,
        "disease": disease,
        "answer": answer
    }