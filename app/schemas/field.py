from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class FieldCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    crop: str = Field(min_length=2, max_length=100)
    variety: Optional[str] = None
    growth_stage: Optional[str] = None
    planting_date: Optional[date] = None
    area: Optional[float] = None


class FieldResponse(BaseModel):
    id: int
    farm_id: int
    name: str
    crop: str
    variety: Optional[str] = None
    growth_stage: Optional[str] = None
    planting_date: Optional[date] = None
    area: Optional[float] = None

    class Config:
        from_attributes = True