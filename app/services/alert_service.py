from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_risk_alert(
    db: Session,
    field_id: int,
    crop: str,
    disease: str,
    risk_score: float,
    risk_level: str
):
    if risk_level == "low":
        return None

    if risk_level == "high":
        severity = "high"
        title = "High Crop Health Risk"

        message = (
            f"High risk detected for {crop}. "
            f"Possible issue: {disease}. "
            f"Risk score: {risk_score}. "
            "Inspect the field immediately and "
            "consider expert verification."
        )

    else:
        severity = "medium"
        title = "Crop Health Warning"

        message = (
            f"Medium risk detected for {crop}. "
            f"Possible issue: {disease}. "
            f"Risk score: {risk_score}. "
            "Monitor the field closely."
        )

    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.field_id == field_id,
            Alert.severity == severity,
            Alert.is_read == False
        )
        .first()
    )

    if existing_alert:
        return existing_alert

    alert = Alert(
        field_id=field_id,
        type="crop_health_risk",
        severity=severity,
        title=title,
        message=message,
        is_read=False
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def create_forecast_alert(
    db: Session,
    field_id: int,
    crop: str,
    disease: str,
    forecast: dict
):
    """
    Create an alert when future forecast risk
    becomes high.
    """

    highest_risk = 0
    highest_day = None

    for day in forecast.get("daily", []):

        score = day.get("risk_score", 0)

        if score > highest_risk:
            highest_risk = score
            highest_day = day.get("date")

    # Only create forecast alert for high risk
    if highest_risk < 70:
        return None

    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.field_id == field_id,
            Alert.type == "forecast_risk",
            Alert.is_read == False
        )
        .first()
    )

    if existing_alert:
        return existing_alert

    alert = Alert(
        field_id=field_id,
        type="forecast_risk",
        severity="high",
        title="Upcoming Crop Health Risk",
        message=(
            f"Forecast indicates high risk for {crop} "
            f"related to {disease}. "
            f"Highest predicted risk is "
            f"{round(highest_risk, 2)} "
            f"around {highest_day}. "
            "Monitor the field closely and "
            "consider preventive action."
        ),
        is_read=False
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert