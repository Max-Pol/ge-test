import asyncio
from typing import Dict, List, Optional

import aiohttp  # Add this import at the top with other imports
from requests_html import AsyncHTMLSession

from .exceptions import WeatherScraperRequestError


async def get_city_info(name: str) -> Optional[dict]:
    """
    Get the city information from weather.com for a given city name asynchronously.

    Args:
        name (str): Name of the city to search for

    Returns:
        Optional[dict]: A dictionary containing city information if found, None otherwise.
            The dictionary has the following structure:
            {
                "name": str,      # Full city name including region/country
                "coordinate": str, # Latitude and longitude in format "lat,lon"
                "placeID": str    # Unique identifier for the location
            }
    """
    url = "https://weather.com/api/v1/p/redux-dal"
    payload = [
        {
            "name": "getSunV3LocationSearchUrlConfig",
            "params": {"query": name, "language": "en-US", "locationType": "locale"},
        }
    ]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()

                location = data["dal"]["getSunV3LocationSearchUrlConfig"][
                    f"language:en-US;locationType:locale;query:{name}"
                ]["data"]["location"]

                return {
                    "name": location["address"][0],
                    "coordinate": f"{location['latitude'][0]},{location['longitude'][0]}",
                    "placeID": location["placeId"][0],
                }

    except Exception as e:
        print(f"Error fetching city ID: {e}")
        return None


async def get_city_weather(place_id: str) -> Optional[Dict[str, str | int]]:
    """
    Get weather information for a given city asynchronously.

    Args:
        city (str): Name of the city to get weather for

    Returns:
        Optional[Dict[str, str | int]]: Dictionary containing weather information or None if city not found
    """
    # Fetch weather data
    asession = AsyncHTMLSession()
    url = f"https://weather.com/weather/today/l/{place_id}?unit=m"  # unit in celsius

    try:
        r = await asession.get(url)

        # Find temperature
        temp_str = r.html.find("span[data-testid='TemperatureValue']", first=True).text
        temp_int = int(temp_str.strip("°"))

        # Find weather phrase
        weather_condition = r.html.find("div[data-testid='wxPhrase']", first=True).text

        return {
            "placeID": place_id,
            "temperature_celsius": temp_int,
            "weather_condition": weather_condition.lower(),
        }
    except Exception as e:
        raise WeatherScraperRequestError(
            f"Error fetching weather data for {place_id}: {e}"
        )
    finally:
        await asession.close()


async def get_city_weathers(city_entries: List[Dict]) -> List[Dict]:
    """
    Get weather information for multiple cities asynchronously and add it to each entry.

    Args:
        city_entries (List[Dict]): List of dictionaries containing city information,
            each dict must have a 'placeID' key

    Returns:
        List[Dict]: List of dictionaries with added weather information
    """
    # Create a copy of the input list. Be aware that this is a shallow copy...
    results = city_entries.copy()

    # Create tasks for fetching weather data
    tasks = [get_city_weather(entry["placeID"]) for entry in city_entries]
    weather_data = await asyncio.gather(*tasks)

    # Add weather data to each entry
    for entry, weather in zip(results, weather_data):
        if weather is not None:
            entry.update(weather)

    return results
