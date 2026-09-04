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


class Monitoring(Base):
    __tablename__ = "monitoring"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    diagnosis_id = Column(
        Integer,
        ForeignKey("diagnoses.id"),
        nullable=False
    )

    # Image stored directly in PostgreSQL
    image_data = Column(
        LargeBinary,
        nullable=True
    )

    # MIME type such as image/jpeg, image/png
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

    comparison = Column(
        String(50),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    diagnosis = relationship(
        "Diagnosis",
        backref="monitoring_records"
    )