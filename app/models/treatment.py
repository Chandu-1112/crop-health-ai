from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(
        Integer,
        ForeignKey("diagnoses.id"),
        nullable=False
    )

    recommendation = Column(Text, nullable=False)
    treatment_type = Column(String(50), nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(String(100), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    diagnosis = relationship(
        "Diagnosis",
        backref="treatments"
    )