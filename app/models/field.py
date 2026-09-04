from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)

    name = Column(String(100), nullable=False)
    crop = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=True)
    growth_stage = Column(String(100), nullable=True)
    planting_date = Column(Date, nullable=True)
    area = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", backref="fields")