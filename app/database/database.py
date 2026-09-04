from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def ensure_database_schema():
    """
    Ensures required database columns exist.
    This is a simple schema fix for the deployed hackathon backend.
    """
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE diagnoses
                ADD COLUMN IF NOT EXISTS image_type VARCHAR(100);
                """
            )
        )

