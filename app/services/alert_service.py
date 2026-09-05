from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_risk_alert(
    db: Session,
    field_id: int,
    crop: str,
    disease: str,
    risk_score: float,
    risk_level: str,
    language: str = "en",
):
    if risk_level == "low":
        return None

    labels = {
        "en": ("High Crop Health Risk", "Crop Health Warning", "High", "Medium", "Inspect the field immediately and consider expert verification.", "Monitor the field closely."),
        "te": ("పంట ఆరోగ్యానికి అధిక ప్రమాదం", "పంట ఆరోగ్య హెచ్చరిక", "అధిక", "మధ్యస్థ", "వెంటనే పొలాన్ని పరిశీలించి నిపుణుల నిర్ధారణ పొందండి.", "పొలాన్ని జాగ్రత్తగా గమనించండి."),
        "hi": ("फसल स्वास्थ्य का उच्च जोखिम", "फसल स्वास्थ्य चेतावनी", "उच्च", "मध्यम", "तुरंत खेत की जांच करें और विशेषज्ञ से पुष्टि लें.", "खेत की करीब से निगरानी करें।"),
    }.get(language, None) or (
        "High Crop Health Risk", "Crop Health Warning", "High", "Medium",
        "Inspect the field immediately and consider expert verification.",
        "Monitor the field closely.",
    )

    if risk_level == "high":
        severity = "high"
        title = labels[0]

    else:
        severity = "medium"
        title = labels[1]

    # The same calculated risk can be requested repeatedly (for example when
    # the recommendations page is refreshed).  Read state is not part of the
    # event identity: marking an alert read must not make it eligible for an
    # identical alert on the next request.
    message = (
        f"{labels[2] if severity == 'high' else labels[3]} risk detected for {crop}. "
        f"Possible issue: {disease}. "
        f"Risk score: {risk_score}. "
        + (
            labels[4]
            if severity == "high"
            else labels[5]
        )
    )

    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.field_id == field_id,
            Alert.type == "crop_health_risk",
            Alert.message == message
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
    forecast: dict,
    language: str = "en",
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

    labels = {
        "en": ("Upcoming Crop Health Risk", "Forecast indicates high risk for", "related to", "Highest predicted risk is", "around", "Monitor the field closely and consider preventive action."),
        "te": ("రాబోయే పంట ఆరోగ్య ప్రమాదం", "అంచనా ప్రకారం అధిక ప్రమాదం", "దీనికి సంబంధించినది", "అంచనా వేసిన గరిష్ఠ ప్రమాదం", "సమీపంలో", "పొలాన్ని జాగ్రత్తగా గమనించి నివారణ చర్యలు తీసుకోండి."),
        "hi": ("आने वाला फसल स्वास्थ्य जोखिम", "पूर्वानुमान में उच्च जोखिम", "से संबंधित", "अनुमानित सबसे अधिक जोखिम", "के आसपास", "खेत की करीब से निगरानी करें और रोकथाम की कार्रवाई करें।"),
    }.get(language, None) or (
        "Upcoming Crop Health Risk", "Forecast indicates high risk for", "related to",
        "Highest predicted risk is", "around", "Monitor the field closely and consider preventive action.",
    )
    message = (
        f"{labels[1]} {crop} "
        f"{labels[2]} {disease}. "
        f"{labels[3]} "
        f"{round(highest_risk, 2)} "
        f"{labels[4]} {highest_day}. "
        f"{labels[5]}"
    )

    # A forecast alert represents this exact forecast result, not its unread
    # state.  A changed score, disease, or forecast day therefore remains a
    # new alert while refreshing an unchanged forecast is idempotent.
    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.field_id == field_id,
            Alert.type == "forecast_risk",
            Alert.message == message
        )
        .first()
    )

    if existing_alert:
        return existing_alert

    alert = Alert(
        field_id=field_id,
        type="forecast_risk",
        severity="high",
        title=labels[0],
        message=message,
        is_read=False
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert