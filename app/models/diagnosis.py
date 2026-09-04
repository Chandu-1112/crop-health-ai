from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    LargeBinary
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    field_id = Column(
        Integer,
        ForeignKey("fields.id"),
        nullable=False
    )

    image_url = Column(
        String(500),
        nullable=True
    )

    image_data = Column(
        LargeBinary,
        nullable=True
    )

    image_type = Column(
        String(100),
        nullable=True
    )

    disease = Column(
        String(150),
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=True
    )

    severity = Column(
        String(50),
        nullable=True
    )

    affected_area = Column(
        Float,
        nullable=True
    )

    diagnosis_source = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(50),
        default="pending"
    )

    explanation = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    field = relationship(
        "Field",
        backref="diagnoses"
    )