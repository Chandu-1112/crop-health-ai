from typing import Dict, Any
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import json


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _fetch_open_meteo(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch weather data from Open-Meteo.
    No API key is required.
    """

    query = urlencode(params)
    url = f"{OPEN_METEO_URL}?{query}"

    try:
        with urlopen(url, timeout=15) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)

    except HTTPError as e:
        raise Exception(
            f"Open-Meteo HTTP error: {e.code}"
        )

    except URLError as e:
        raise Exception(
            f"Open-Meteo connection error: {e.reason}"
        )

    except Exception as e:
        raise Exception(
            f"Failed to fetch weather data: {str(e)}"
        )


def get_weather(
    latitude: float,
    longitude: float
):
    """
    Get current weather for a field location.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "timezone": "auto"
    }

    data = _fetch_open_meteo(params)

    current = data.get("current")

    if not current:
        raise Exception(
            "Current weather data not available"
        )

    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get(
            "relative_humidity_2m"
        ),
        "rainfall": current.get(
            "precipitation"
        ),
        "wind_speed": current.get(
            "wind_speed_10m"
        ),
        "weather_code": current.get(
            "weather_code"
        ),
        "time": current.get("time"),
        "timezone": data.get("timezone")
    }


def get_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = 14
):
    """
    Get daily weather forecast.

    Returns a list compatible with
    calculate_forecast_risk().
    """

    days = max(1, min(days, 16))

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

    data = _fetch_open_meteo(params)

    daily = data.get("daily")

    if not daily:
        raise Exception(
            "Weather forecast data not available"
        )

    dates = daily.get("time", [])
    temperatures_max = daily.get(
        "temperature_2m_max", []
    )
    temperatures_min = daily.get(
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

    for i, date in enumerate(dates):

        forecast.append({
            "date": date,

            "temperature_max": (
                temperatures_max[i]
                if i < len(temperatures_max)
                else None
            ),

            "temperature_min": (
                temperatures_min[i]
                if i < len(temperatures_min)
                else None
            ),

            "humidity": (
                humidity[i]
                if i < len(humidity)
                else None
            ),

            "rainfall": (
                rainfall[i]
                if i < len(rainfall)
                else None
            ),

            "wind_speed": (
                wind_speed[i]
                if i < len(wind_speed)
                else None
            )
        })

    return forecast

