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
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS role VARCHAR(30) NOT NULL DEFAULT 'farmer';
                """
            )
        )


def ensure_default_admin_user():
    """Create the default admin account if it does not already exist."""
    from app.core.security import hash_password
    from app.models.user import User

    db = SessionLocal()
    try:
        existing_user = (
            db.query(User)
            .filter(User.mobile == "8330965648")
            .first()
        )

        if existing_user:
            if existing_user.role != "admin":
                existing_user.role = "admin"
                existing_user.name = "Admin"
                existing_user.password_hash = hash_password("admin123")
                db.commit()
            return existing_user

        admin_user = User(
            name="Admin",
            mobile="8330965648",
            password_hash=hash_password("admin123"),
            language="en",
            role="admin",
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        return admin_user
    finally:
        db.close()
