import requests


def get_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "rain,"
            "wind_speed_10m"
        ),
        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(
            "Failed to fetch current weather"
        )

    data = response.json()

    current = data.get("current", {})

    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get(
            "relative_humidity_2m"
        ),
        "rainfall": current.get("rain"),
        "wind_speed": current.get(
            "wind_speed_10m"
        )
    }


def get_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = 14
):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "relative_humidity_2m_mean,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),
        "forecast_days": days,
        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(
            "Failed to fetch weather forecast"
        )

    data = response.json()
    daily = data.get("daily", {})

    dates = daily.get("time", [])
    max_temperature = daily.get(
        "temperature_2m_max", []
    )
    min_temperature = daily.get(
        "temperature_2m_min", []
    )
    humidity = daily.get(
        "relative_humidity_2m_mean", []
    )
    rainfall = daily.get(
        "precipitation_sum", []
    )
    wind_speed = daily.get(
        "wind_speed_10m_max", []
    )

    forecast = []

    for i in range(len(dates)):
        forecast.append({
            "date": dates[i],
            "temperature_max": max_temperature[i],
            "temperature_min": min_temperature[i],
            "humidity": humidity[i],
            "rainfall": rainfall[i],
            "wind_speed": wind_speed[i]
        })

    return forecast