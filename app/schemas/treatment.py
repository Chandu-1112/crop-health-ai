from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TreatmentCreate(BaseModel):
    recommendation: str
    treatment_type: Optional[str] = None
    started_at: Optional[datetime] = None


class TreatmentUpdate(BaseModel):
    result: Optional[str] = Field(
        default=None,
        pattern="^(effective|partially_effective|not_effective|unknown)$"
    )

    started_at: Optional[datetime] = None


class TreatmentResponse(BaseModel):
    id: int
    diagnosis_id: int
    recommendation: str
    treatment_type: Optional[str] = None
    started_at: Optional[datetime] = None
    result: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True