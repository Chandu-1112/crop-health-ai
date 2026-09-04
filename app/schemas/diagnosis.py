from pydantic import BaseModel
from typing import Optional


class DiagnosisResponse(BaseModel):
    id: int
    field_id: int
    image_url: Optional[str] = None
    disease: str
    confidence: Optional[float] = None
    severity: Optional[str] = None
    affected_area: Optional[float] = None
    diagnosis_source: Optional[str] = None
    status: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

