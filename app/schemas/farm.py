from pydantic import BaseModel, Field
from typing import Optional


class FarmCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    area: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmResponse(BaseModel):
    id: int
    name: str
    area: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
        