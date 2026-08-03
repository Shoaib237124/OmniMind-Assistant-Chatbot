import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import Field

load_dotenv()


@tool
def get_weather(
    city: str = Field(
        description="The city name to fetch current weather for, e.g., London, New York, Tokyo"
    )
) -> str:
    """
    Get the current weather conditions for a specified city.
    """
    key = os.getenv("WEATHER_API_KEY")

    if not key:
        return "Error: WEATHER_API_KEY environment variable is not set."

    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q={city.strip()}"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Handle WeatherAPI error responses (e.g., city not found)
        if "error" in data:
            return f"Error from Weather API: {data['error'].get('message', 'Failed to fetch weather data.')}"

        current = data.get("current", {})
        temp_c = current.get("temp_c", "N/A")
        condition = current.get("condition", {}).get("text", "N/A")
        humidity = current.get("humidity", "N/A")
        wind_kph = current.get("wind_kph", "N/A")

        return (
            f"Weather in {city.strip().title()}:\n"
            f"Temperature: {temp_c}°C\n"
            f"Condition: {condition}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_kph} km/h"
        )

    except Exception as e:
        return f"Error retrieving weather for '{city}': {str(e)}"