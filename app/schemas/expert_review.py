from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExpertReviewCreate(BaseModel):
    notes: Optional[str] = None


class ExpertReviewUpdate(BaseModel):
    status: str
    expert_diagnosis: Optional[str] = None
    expert_notes: Optional[str] = None


class ExpertReviewResponse(BaseModel):
    id: int
    diagnosis_id: int
    status: str
    expert_diagnosis: Optional[str] = None
    expert_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    diagnosis: Optional[dict] = None
    farmer_name: Optional[str] = None
    crop: Optional[str] = None

    class Config:
        from_attributes = True