from typing import Dict, Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import time


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Cache durations
CURRENT_WEATHER_CACHE_SECONDS = 1800      # 30 minutes
FORECAST_CACHE_SECONDS = 21600            # 6 hours

# In-memory cache
_weather_cache: Dict[str, Dict[str, Any]] = {}
_forecast_cache: Dict[str, Dict[str, Any]] = {}


def _cache_key(latitude: float, longitude: float) -> str:
    """
    Create a stable cache key for a location.
    """
    return f"{round(float(latitude), 4)}:{round(float(longitude), 4)}"


def _fetch_open_meteo(
    params: Dict[str, Any],
    retries: int = 2
) -> Dict[str, Any]:
    """
    Fetch weather data from Open-Meteo.

    Uses a User-Agent and retries temporary errors.
    """

    query = urlencode(params)
    url = f"{OPEN_METEO_URL}?{query}"

    request = Request(
        url,
        headers={
            "User-Agent": (
                "CropHealthAI/1.0 "
                "(hackathon agricultural weather application)"
            ),
            "Accept": "application/json"
        }
    )

    last_error = None

    for attempt in range(retries + 1):

        try:
            with urlopen(request, timeout=15) as response:
                data = response.read().decode("utf-8")
                return json.loads(data)

        except HTTPError as e:
            last_error = e

            # 429 = rate limited.
            # Wait before retrying.
            if e.code == 429:
                if attempt < retries:
                    time.sleep(2 * (attempt + 1))
                    continue

                raise Exception(
                    "Open-Meteo rate limit reached. "
                    "Please try again shortly."
                )

            raise Exception(
                f"Open-Meteo HTTP error: {e.code}"
            )

        except URLError as e:
            last_error = e

            if attempt < retries:
                time.sleep(1 * (attempt + 1))
                continue

            raise Exception(
                f"Open-Meteo connection error: {e.reason}"
            )

        except Exception as e:
            last_error = e

            if attempt < retries:
                time.sleep(1)
                continue

            raise Exception(
                f"Failed to fetch weather data: {str(e)}"
            )

    raise Exception(
        f"Failed to fetch weather data: {str(last_error)}"
    )


def get_weather(
    latitude: float,
    longitude: float,
    force_refresh: bool = False
):
    """
    Get current weather for a field location.

    Results are cached for 10 minutes so repeated
    frontend requests do not repeatedly hit Open-Meteo.
    """

    key = _cache_key(latitude, longitude)

    # Check cache
    cached = _weather_cache.get(key)

    if cached and not force_refresh:
        age = time.time() - cached["timestamp"]

        if age < CURRENT_WEATHER_CACHE_SECONDS:
            return cached["data"]

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

    try:
        data = _fetch_open_meteo(params)
    except Exception as error:
        if cached:
            return cached["data"]
        raise error

    current = data.get("current")

    if not current:
        raise Exception(
            "Current weather data not available"
        )

    weather = {
        "temperature": current.get(
            "temperature_2m"
        ),
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

    # Save in cache
    _weather_cache[key] = {
        "timestamp": time.time(),
        "data": weather
    }

    return weather


def get_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = 14,
    force_refresh: bool = False
):
    """
    Get daily weather forecast.

    Results are cached for 30 minutes.
    """

    days = max(1, min(days, 16))

    key = f"{_cache_key(latitude, longitude)}:{days}"

    # Check cache
    cached = _forecast_cache.get(key)

    if cached and not force_refresh:
        age = time.time() - cached["timestamp"]

        if age < FORECAST_CACHE_SECONDS:
            return cached["data"]

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

    try:
        data = _fetch_open_meteo(params)
    except Exception as error:
        # Keep the last successful forecast usable during provider throttling.
        # A stale forecast is safer than turning the dashboard into a 500.
        if cached:
            return cached["data"]
        raise error

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

    # Save in cache
    _forecast_cache[key] = {
        "timestamp": time.time(),
        "data": forecast
    }

    return forecast
