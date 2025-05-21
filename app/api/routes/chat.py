from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import CurrentUser, SessionDep
from app.chat.chat import WeatherAgent, WeatherData
from app.core.config import settings
from app.weather.city import get_city_weathers
from app.weather.scraper import WeatherScraper

router = APIRouter(prefix="/chat", tags=["chat"])


class SummaryResponse(BaseModel):
    summary: str


class AskResponse(BaseModel):
    """Represents the answer to a weather-related question."""

    answer: str
    matching_cities: List[str]


class AskRequest(BaseModel):
    """Request model for asking weather-related questions."""

    question: str


@router.post("/summary", response_model=SummaryResponse)
async def create_summary(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve weather summary for favorite cities.
    """
    try:
        # Fetch user favorite cities
        w = WeatherScraper(current_user.weather_id_token)
        favorite_cities = await w.get_user_favorite_cities()
        favorite_cities = await get_city_weathers(favorite_cities)

        # Convert to WeatherData
        weather_data = [
            WeatherData(
                city=city["name"],
                weather_condition=city["weather_condition"],
                temperature=city["temperature_celsius"],
            )
            for city in favorite_cities
        ]

        # Generate Summary
        weather_agent = WeatherAgent(settings.OPENAI_API_KEY)
        summary = weather_agent.summarize(weather_data)

        return SummaryResponse(summary=summary)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate weather summary: {str(e)}"
        )


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest, session: SessionDep, current_user: CurrentUser):
    """
    Answer a weather-related question about favorite cities.
    """
    try:
        # Fetch user favorite cities
        w = WeatherScraper(current_user.weather_id_token)
        favorite_cities = await w.get_user_favorite_cities()
        favorite_cities = await get_city_weathers(favorite_cities)

        # Convert to WeatherData
        weather_data = [
            WeatherData(
                city=city["name"],
                weather_condition=city["weather_condition"],
                temperature=city["temperature_celsius"],
            )
            for city in favorite_cities
        ]

        # Ask
        weather_agent = WeatherAgent(settings.OPENAI_API_KEY)
        return weather_agent.ask(request.question, weather_data)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to answer weather question: {str(e)}"
        )
