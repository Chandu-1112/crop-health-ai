from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class ExpertReview(Base):
    __tablename__ = "expert_reviews"

    id = Column(Integer, primary_key=True, index=True)

    diagnosis_id = Column(
        Integer,
        ForeignKey("diagnoses.id"),
        nullable=False
    )

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    expert_diagnosis = Column(
        String(150),
        nullable=True
    )

    expert_notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    diagnosis = relationship(
        "Diagnosis",
        backref="expert_reviews"
    )