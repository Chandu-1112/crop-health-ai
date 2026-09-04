from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MonitoringResponse(BaseModel):
    id: int
    diagnosis_id: int
    image_url: Optional[str] = None
    disease: str
    confidence: Optional[float] = None
    severity: Optional[str] = None
    affected_area: Optional[float] = None
    comparison: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True