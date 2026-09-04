import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude: float, longitude: float):
    """
    Fetch current weather for the farm/field GPS coordinates.

    Uses Open-Meteo current weather API.
    No API key required.
    """

    try:
        # Validate coordinates
        latitude = float(latitude)
        longitude = float(longitude)

        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid latitude")

        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid longitude")

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
            "timezone": "auto",
        }

        url = f"{OPEN_METEO_URL}?{urlencode(params)}"

        request = Request(
            url,
            headers={
                "User-Agent": "Crop-Health-AI/1.0",
                "Accept": "application/json",
            },
            method="GET",
        )

        with urlopen(request, timeout=15) as response:
            status_code = response.status
            response_data = response.read().decode("utf-8")

        if status_code != 200:
            raise Exception(
                f"Open-Meteo returned HTTP {status_code}"
            )

        data = json.loads(response_data)

        current = data.get("current")

        if not current:
            raise Exception(
                "Open-Meteo response did not contain current weather data"
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "time": current.get("time"),
            "timezone": data.get("timezone"),
            "temperature_unit": (
                data.get("current_units", {})
                .get("temperature_2m", "°C")
            ),
            "humidity_unit": (
                data.get("current_units", {})
                .get("relative_humidity_2m", "%")
            ),
            "precipitation_unit": (
                data.get("current_units", {})
                .get("precipitation", "mm")
            ),
            "wind_speed_unit": (
                data.get("current_units", {})
                .get("wind_speed_10m", "km/h")
            ),
        }

    except HTTPError as error:
        print(
            "Open-Meteo HTTP error:",
            error.code,
            error.reason
        )

        raise Exception(
            f"Weather service returned HTTP {error.code}"
        )

    except URLError as error:
        print(
            "Open-Meteo connection error:",
            error.reason
        )

        raise Exception(
            "Unable to connect to weather service"
        )

    except json.JSONDecodeError as error:
        print(
            "Open-Meteo JSON error:",
            error
        )

        raise Exception(
            "Weather service returned invalid data"
        )

    except Exception as error:
        print(
            "Weather service error:",
            error
        )

        raise Exception(
            f"Failed to fetch current weather: {error}"
        )

