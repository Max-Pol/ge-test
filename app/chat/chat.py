from typing import List

from openai import OpenAI
from pydantic import BaseModel

from .prompts import WEATHER_QUERY_PROMPT, WEATHER_SUMMARY_PROMPT

MODEL = "gpt-4.1-nano"


class WeatherAgentError(Exception):
    """Custom exception for weather agent related errors."""

    pass


class WeatherData(BaseModel):
    """Hold weather information for a city."""

    city: str
    weather_condition: str  # e.g., "sunny", "rainy", "cloudy"
    temperature: float  # in Celsius


class AskResponse(BaseModel):
    """Represents the answer to a weather-related question."""

    answer: str
    matching_cities: List[str]


class WeatherAgent:
    """Agent responsible for handling weather-related queries and summaries."""

    def __init__(self, openai_api_key: str):
        """Initialize the WeatherAgent with OpenAI client."""
        self.client = OpenAI()

    def summarize(self, cities: List[WeatherData]) -> str:
        """
        Generate a natural language summary of weather conditions for multiple cities using OpenAI's API.

        Args:
            cities: List of WeatherData objects containing weather information for each city

        Returns:
            str: A natural language summary of the weather
        """
        if not cities:
            return "No weather data available to summarize."

        try:
            # Format the prompt
            weather_context = build_weather_context(cities)
            prompt = WEATHER_SUMMARY_PROMPT.format(weather_context=weather_context)

            # Call OpenAI API
            response = self.client.responses.create(
                model=MODEL,
                input=[
                    {
                        "role": "system",
                        "content": prompt,
                    }
                ],
                temperature=0.7,  # Add some creativity while keeping it focused
                max_output_tokens=150,  # Keep summaries concise
            )
            return response.output[0].content[0].text

        except Exception as e:
            # Raise custom exception with original error details
            raise WeatherAgentError(f"Failed to generate weather summary: {str(e)}")

    def ask(self, question: str, cities: List[WeatherData]) -> AskResponse:
        """
        Answer a freeform question about weather in the specified cities.

        Args:
            question: Natural language question about the weather
            cities: List of WeatherData objects containing weather information for each city

        Returns:
            Dictionary containing the answer to the weather question
        """
        if not cities:
            return AskResponse(
                answer="No weather data available to answer the question.",
                matching_cities=[],
            )

        try:
            # Format the prompt
            weather_context = build_weather_context(cities)
            prompt = WEATHER_QUERY_PROMPT.format(weather_context=weather_context)

            # Call OpenAI API
            response = self.client.responses.parse(
                model=MODEL,
                input=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
                text_format=AskResponse,
                temperature=0.7,  # Add some creativity while keeping it focused
                max_output_tokens=150,  # Keep summaries concise
            )

            return response.output_parsed

        except Exception as e:
            # Raise custom exception with original error details
            raise WeatherAgentError(f"Failed to generate weather response: {str(e)}")


def build_weather_context(cities: List[WeatherData]) -> str:
    """
    Build a weather context string from a list of WeatherData objects.

    Args:
        cities: List of WeatherData objects containing weather information for each city

    Returns:
        str: A weather context string
    """
    return "\n".join(
        [
            f"- {city.city}: {city.weather_condition}, {city.temperature}°C"
            for city in cities
        ]
    )
