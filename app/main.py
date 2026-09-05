from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import (
    engine,
    get_db,
    Base,
    ensure_database_schema
)


# ============================================================
# Import all models so SQLAlchemy knows about them
# ============================================================

from app.models.user import User
from app.models.farm import Farm
from app.models.field import Field
from app.models.diagnosis import Diagnosis
from app.models.weather import WeatherData
from app.models.treatment import Treatment
from app.models.alert import Alert
from app.models.monitoring import Monitoring


# ============================================================
# Import routers
# ============================================================

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.farms import router as farms_router
from app.routers.fields import router as fields_router
from app.routers.diagnosis import router as diagnosis_router
from app.routers.weather import router as weather_router
from app.routers.risk import router as risk_router
from app.routers.recommendations import router as recommendations_router
from app.routers.alerts import router as alerts_router
from app.routers.treatments import router as treatments_router
from app.routers.dashboard import router as dashboard_router
from app.routers.forecast import router as forecast_router
from app.routers.monitoring import router as monitoring_router
from app.routers.hotspot import router as hotspot_router
from app.routers.chat import router as chat_router


# ============================================================
# Create database tables
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# Ensure existing database has required columns
# ============================================================

ensure_database_schema()


# ============================================================
# Create FastAPI application
# ============================================================

app = FastAPI(
    title="Crop Health API"
)


# ============================================================
# Include routers
# ============================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(farms_router)
app.include_router(fields_router)
app.include_router(diagnosis_router)
app.include_router(weather_router)
app.include_router(risk_router)
app.include_router(recommendations_router)
app.include_router(alerts_router)
app.include_router(treatments_router)
app.include_router(forecast_router)
app.include_router(dashboard_router)
app.include_router(monitoring_router)
app.include_router(hotspot_router)
app.include_router(chat_router)


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Crop Health Backend Running"
    }


# ============================================================
# Database test endpoint
# ============================================================

@app.get("/test-db")
def test_database(
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("SELECT 1")
    )

    return {
        "database": "connected",
        "result": result.scalar()
    }
