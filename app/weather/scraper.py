import asyncio
from typing import List, Optional

import aiohttp

from .city import get_city_info
from .exceptions import InvalidLoginCredentials, WeatherScraperRequestError

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain;charset=UTF-8",
    "dnt": "1",
    "origin": "https://weather.com",
    "priority": "u=1, i",
    "referer": "https://weather.com/",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}

WEATHER_API_URL = "https://upsx.weather.com"
LOGIN_URL = f"{WEATHER_API_URL}/login"
PREFERENCE_URL = f"{WEATHER_API_URL}/preference"
LOGIN_INVALID_MESSAGE = "use a valid user ID and password"


class WeatherScraper:
    """A class to interact with the Weather.com API with authentication management."""

    def __init__(self, id_token=None):
        """Initialize a new WeatherScraper instance."""
        self.id_token: Optional[str] = id_token
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def _check_authentication(self) -> None:
        """Check if the user is authenticated.

        Raises:
            WeatherScraperRequestError: If the user is not authenticated.
        """
        # if not all([self.id_token, self.access_token, self.refresh_token]):
        if not self.id_token:
            raise WeatherScraperRequestError(
                "User is not authenticated. Please login first."
            )

    async def user_login(self, email, password):
        """Authenticate with the Weather.com API using email and password credentials.

        Args:
            email (str): The email address to use for authentication
            password (str): The password associated with the email account

        Returns:
            - id_token (str): Token containing user identity information

        Raises:
            InvalidLoginCredentials   : If the provided email or password is invalid
            WeatherScraperRequestError: If the request fails or required tokens are missing
        """
        data = f'{{"email":"{email}","password":"{password}"}}'

        async with aiohttp.ClientSession() as session:
            async with session.post(LOGIN_URL, headers=HEADERS, data=data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    if resp.status == 400 and LOGIN_INVALID_MESSAGE in text:
                        raise InvalidLoginCredentials(
                            "Invalid email or password provided"
                        )
                    raise WeatherScraperRequestError(
                        f"Request failed with status code {resp.status}: {text}"
                    )

                cookies = resp.cookies
                access_token = cookies.get("access_token").value
                id_token = cookies.get("id_token").value
                refresh_token = cookies.get("refresh_token").value

                if not access_token or not id_token or not refresh_token:
                    raise WeatherScraperRequestError(
                        "Failed to get access token, id token, or refresh token"
                    )
                self.id_token = id_token
                self.access_token = access_token
                self.refresh_token = refresh_token

        return self.id_token

    async def get_user_preferences(self):
        """Retrieve the authenticated user's preferences from Weather.com.

        Args:
            id_token (str): The ID token obtained from successful login

        Returns:
            dict: A dictionary containing the user's preferences with the following structure:
                - userID (str): Unique identifier for the user
                - locations (list): List of location dictionaries containing the user's favorite cities. Each location
                dictionary has the following structure:
                    - name (str): Full location name including city, region, and country
                    - coordinate (str): Latitude and longitude coordinates in format "lat,lon"
                    - placeID (str): Unique identifier for the location
                    - position (int): User-defined position/order of the favorite location
                - locale (str): User's preferred locale (e.g., "en-US")
                - unit (str): User's preferred unit system (e.g., "Metric")
                - dashboard (list): List of dashboard widgets. Each widget contains:
                    - position (int): Widget position
                    - type (str): Widget type (e.g., "wxlocation")
                    - locations (list): List of locations for the widget
                    - data (list): List of data properties to display (e.g., humidity, wind, airQuality)

            Example return value:
            {
                'userID': '62387279e09545fdb978fb3719aef91b',
                'locations': [
                    {
                        'name': 'Paris, Île-de-France, France',
                        'coordinate': '48.85,2.35',
                        'placeID': 'a5c27da38afe789545e3446ede0bfd5042030764469a6cd4fff4e9468c74d2a7',
                        'position': 4
                    },
                    # ... more locations ...
                ],
                'locale': 'en-US',
                'unit': 'Metric',
                'dashboard': [
                    {
                        'position': 1,
                        'type': 'wxlocation',
                        'locations': [
                            {
                                'name': 'Paris',
                                'userTag': 'Paris',
                                'coordinate': '48.85,2.35',
                                'placeID': 'a5c27da38afe789545e3446ede0bfd5042030764469a6cd4fff4e9468c74d2a7',
                                'position': 1
                            }
                        ],
                        'data': [
                            {'position': 1, 'properties': {'condition': 'humidity'}},
                            {'position': 2, 'properties': {'condition': 'wind'}},
                            {'position': 3, 'properties': {'condition': 'airQuality'}}
                        ]
                    }
                ]
            }

        Raises:
            WeatherScraperRequestError: If the request fails or returns invalid data
        """
        self._check_authentication()

        cookies = {
            "id_token": self.id_token,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                PREFERENCE_URL, cookies=cookies, headers=HEADERS
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise WeatherScraperRequestError(
                        f"Failed to retrieve favorite cities. Status code: {resp.status}, Response: {text}"
                    )

                try:
                    return await resp.json()
                except (KeyError, ValueError) as e:
                    raise WeatherScraperRequestError(
                        f"Failed to parse preferences response: {str(e)}"
                    )

    async def get_user_favorite_cities(self):
        """Retrieve the authenticated user's favorite cities from Weather.com.

        Args:
            id_token (str): The ID token obtained from successful login

        Returns:
            list: A list of location dictionaries containing the user's favorite cities. Each location
            dictionary has the following structure:
                - name (str): Full location name including city, region, and country
                - coordinate (str): Latitude and longitude coordinates in format "lat,lon"
                - placeID (str): Unique identifier for the location
                - position (int): User-defined position/order of the favorite location

            Example return value:
            [
                {
                    'name': 'Birmingham, England, United Kingdom',
                    'coordinate': '52.48,-1.90',
                    'placeID': 'e22e5ef714ce1dd78d0094a96eca7a476b97d17e3d4b99aaa7e84971e35911c8',
                    'position': 2
                },
                {
                    'name': 'Madrid, Madrid, Spain',
                    'coordinate': '40.42,-3.70',
                    'placeID': 'f620d7fe58f453124aa71caa578d94f09a298b74f2e9bd519413ad3d9ce6a771',
                    'position': 1
                }
            ]

        Raises:
            WeatherScraperRequestError: If the request fails or returns invalid data
        """
        user_preferences = await self.get_user_preferences()
        return user_preferences.get("locations", [])

    async def add_user_favorite_cities(self, city_names: List[str]) -> dict:
        """Add multiple favorite cities to the user's preferences.

        Args:
            city_names (List[str]): List of city names to add

        Returns:
            dict: The updated user preferences after adding the new cities

        Raises:
            WeatherScraperRequestError: If the request fails or returns invalid data
        """
        # Get current preferences
        preferences = await self.get_user_preferences()
        locations = preferences.get("locations", [])

        # Get city infos in parallel
        city_infos = await asyncio.gather(
            *[get_city_info(city_name) for city_name in city_names],
            return_exceptions=True,
        )

        # Filter out any failed city lookups and raise error if any failed
        failed_cities = []
        valid_city_infos = []
        for city_name, city_info in zip(city_names, city_infos):
            if isinstance(city_info, Exception) or not city_info:
                failed_cities.append(city_name)
            else:
                valid_city_infos.append(city_info)

        if failed_cities:
            raise WeatherScraperRequestError(
                f"Failed to find city info for: {', '.join(failed_cities)}"
            )

        # Remove duplicates based on placeID
        existing_place_ids = {loc["placeID"] for loc in locations}
        valid_city_infos = [
            city_info
            for city_info in valid_city_infos
            if city_info["placeID"] not in existing_place_ids
        ]

        # Get the next position number (max position + 1)
        current_positions = [loc.get("position", 0) for loc in locations]
        next_position = max(current_positions, default=0) + 1

        # Add new cities to locations with incremental positions
        for i, city_info in enumerate(valid_city_infos):
            new_location = {**city_info, "position": next_position + i}
            locations.append(new_location)
        if locations:
            preferences["locations"] = locations

        # Update preferences
        cookies = {
            "id_token": self.id_token,
        }

        async with aiohttp.ClientSession() as session:
            async with session.put(
                PREFERENCE_URL, cookies=cookies, headers=HEADERS, json=preferences
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise WeatherScraperRequestError(
                        f"Failed to update favorite cities. Status code: {resp.status}, Response: {text}"
                    )

        return locations
