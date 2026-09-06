from typing import Optional, List, Dict


def calculate_daily_risk(
    current_risk_score: float,
    humidity: Optional[float] = None,
    rainfall: Optional[float] = None,
    temperature: Optional[float] = None
):
    """
    Calculate the additional risk caused by
    forecast weather conditions.
    """

    weather_factor = 0

    # Humidity
    if humidity is not None:
        if humidity >= 85:
            weather_factor += 15
        elif humidity >= 75:
            weather_factor += 10
        elif humidity >= 65:
            weather_factor += 5

    # Rainfall
    if rainfall is not None:
        if rainfall >= 15:
            weather_factor += 12
        elif rainfall >= 7:
            weather_factor += 8
        elif rainfall >= 3:
            weather_factor += 4

    # Temperature
    if temperature is not None:
        if 20 <= temperature <= 30:
            weather_factor += 5

    risk_score = min(
        current_risk_score + weather_factor,
        100
    )

    return {
        "risk_score": round(risk_score, 2),
        "risk_level": get_risk_level(risk_score)
    }


def calculate_forecast_risk(
    current_risk_score: float,
    forecast: List[Dict]
):
    """
    Calculate crop-health risk for each
    forecast day and summarize 3, 5 and 7 days.
    """

    daily_forecast = []

    for day in forecast:

        temperature = None

        if (
            day.get("temperature_max") is not None
            and day.get("temperature_min") is not None
        ):
            temperature = (
                day["temperature_max"]
                + day["temperature_min"]
            ) / 2

        risk = calculate_daily_risk(
            current_risk_score=current_risk_score,
            humidity=day.get("humidity"),
            rainfall=day.get("rainfall"),
            temperature=temperature
        )

        daily_forecast.append({
            "date": day.get("date"),
            "temperature": round(
                temperature, 2
            ) if temperature is not None else None,
            "humidity": day.get("humidity"),
            "rainfall": day.get("rainfall"),
            "wind_speed": day.get("wind_speed"),
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"]
        })

    return {
        "3_day": get_period_summary(
            daily_forecast,
            3
        ),
        "5_day": get_period_summary(
            daily_forecast,
            5
        ),
        "7_day": get_period_summary(
            daily_forecast,
            7
        ),
        "daily": daily_forecast
    }


def get_period_summary(
    daily_forecast: List[Dict],
    days: int
):
    period = daily_forecast[:days]

    if not period:
        return {
            "risk_score": 0,
            "risk_level": "low"
        }

    highest_risk = max(
        period,
        key=lambda x: x["risk_score"]
    )

    average_risk = sum(
        day["risk_score"]
        for day in period
    ) / len(period)

    return {
        "risk_score": round(
            average_risk,
            2
        ),
        "highest_risk_score": highest_risk[
            "risk_score"
        ],
        "highest_risk_level": highest_risk[
            "risk_level"
        ],
        "risk_level": get_risk_level(
            average_risk
        )
    }


def get_risk_level(score: float):

    if score >= 70:
        return "high"

    if score >= 40:
        return "medium"

    return "low"