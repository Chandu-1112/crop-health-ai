def calculate_risk(
    disease: str,
    confidence: float,
    severity: str,
    temperature: float | None = None,
    humidity: float | None = None,
    rainfall: float | None = None,
    growth_stage: str | None = None
):
    score = 0.0

    # --------------------------------
    # AI confidence
    # --------------------------------

    if confidence >= 0.85:
        score += 35
    elif confidence >= 0.65:
        score += 25
    elif confidence >= 0.40:
        score += 15

    # --------------------------------
    # Current disease severity
    # --------------------------------

    if severity.lower() == "high":
        score += 30
    elif severity.lower() == "medium":
        score += 20
    elif severity.lower() == "low":
        score += 10

    # --------------------------------
    # Humidity
    # --------------------------------

    if humidity is not None:

        if humidity >= 80:
            score += 20

        elif humidity >= 65:
            score += 10

    # --------------------------------
    # Rainfall
    # --------------------------------

    if rainfall is not None:

        if rainfall >= 10:
            score += 10

        elif rainfall >= 3:
            score += 5

    # --------------------------------
    # Temperature
    # --------------------------------

    if temperature is not None:

        if 20 <= temperature <= 30:
            score += 5

    # --------------------------------
    # Limit score
    # --------------------------------

    score = min(score, 100)

    # --------------------------------
    # Risk level
    # --------------------------------

    if score >= 70:
        risk_level = "high"

    elif score >= 40:
        risk_level = "medium"

    else:
        risk_level = "low"

    return {
        "disease": disease,
        "risk_score": round(score, 2),
        "risk_level": risk_level
    }