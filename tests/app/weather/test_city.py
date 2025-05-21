from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.weather.city import get_city_info, get_city_weather, get_city_weathers

# Sample test data
MOCK_CITY_RESPONSE = {
    "dal": {
        "getSunV3LocationSearchUrlConfig": {
            "language:en-US;locationType:locale;query:London": {
                "data": {
                    "location": {
                        "address": ["London, UK"],
                        "latitude": ["51.5074"],
                        "longitude": ["-0.1278"],
                        "placeId": ["london-uk"],
                    }
                }
            }
        }
    }
}


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
async def test_get_city_info(mock_post):
    # Mock the aiohttp response
    mock_response = AsyncMock()
    mock_response.json.return_value = MOCK_CITY_RESPONSE
    mock_response.__aenter__.return_value = mock_response
    mock_post.return_value.__aenter__.return_value = mock_response

    result = await get_city_info("London")
    assert result == {
        "name": "London, UK",
        "coordinate": "51.5074,-0.1278",
        "placeID": "london-uk",
    }


@pytest.mark.asyncio
@patch("app.weather.city.AsyncHTMLSession")
async def test_get_city_weather(mock_session):
    # Create mock elements with text attributes
    mock_temp_element = Mock()
    mock_temp_element.text = "20°"
    mock_weather_element = Mock()
    mock_weather_element.text = "Sunny"

    # Create mock HTML response with sync find method
    mock_html = Mock()

    def find_side_effect(selector, first=False):
        if selector == "span[data-testid='TemperatureValue']" and first:
            return mock_temp_element
        elif selector == "div[data-testid='wxPhrase']" and first:
            return mock_weather_element
        return []

    mock_html.find.side_effect = find_side_effect

    # Create mock response with HTML attribute
    mock_r = AsyncMock()
    mock_r.html = mock_html

    # Create an async mock for the get method that returns our mock response
    mock_get = AsyncMock(return_value=mock_r)

    # Create an async mock for the session instance
    mock_session_instance = AsyncMock()
    mock_session_instance.get = mock_get
    mock_session_instance.close = AsyncMock()

    # Make the session constructor return our mock instance
    mock_session.return_value = mock_session_instance

    result = await get_city_weather("london-uk")
    assert result == {
        "placeID": "london-uk",
        "temperature_celsius": 20,
        "weather_condition": "sunny",
    }

    # Verify the mocks were called correctly
    mock_get.assert_called_once()
    mock_session_instance.close.assert_called_once()
    assert mock_html.find.call_count == 2  # Verify find was called twice


@pytest.mark.asyncio
@patch("app.weather.city.get_city_weather")
async def test_get_city_weathers(mock_get_city_weather):
    # Mock weather data for two cities
    mock_get_city_weather.side_effect = [
        {
            "placeID": "london-uk",
            "temperature_celsius": 20,
            "weather_condition": "sunny",
        },
        {
            "placeID": "paris-fr",
            "temperature_celsius": 22,
            "weather_condition": "cloudy",
        },
    ]
    city_entries = [
        {"placeID": "london-uk", "name": "London, UK"},
        {"placeID": "paris-fr", "name": "Paris, France"},
    ]
    results = await get_city_weathers(city_entries)
    assert results[0]["temperature_celsius"] == 20
    assert results[0]["weather_condition"] == "sunny"
    assert results[1]["temperature_celsius"] == 22
    assert results[1]["weather_condition"] == "cloudy"
