from typing import Dict, List

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.deps import CurrentUser, SessionDep
from app.repository import create_or_update_cities
from app.weather.city import get_city_weathers
from app.weather.scraper import WeatherScraper

router = APIRouter(prefix="/cities", tags=["cities"])


class FavoriteCitiesRequest(BaseModel):
    cities: List[str]


@router.get("/favorites")
async def get_favorites(session: SessionDep, current_user: CurrentUser) -> List[Dict]:
    """
    Retrieve favorite cities.
    """
    w = WeatherScraper(current_user.weather_id_token)
    favorite_cities = await w.get_user_favorite_cities()
    favorite_cities = await get_city_weathers(favorite_cities)
    return favorite_cities


@router.post("/favorites", status_code=status.HTTP_201_CREATED)
async def add_user_favorite_cities(
    request: FavoriteCitiesRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> List[Dict]:
    """
    Add new favorite cities for the user.
    """
    w = WeatherScraper(current_user.weather_id_token)
    favorite_cities = await w.add_user_favorite_cities(request.cities)
    return favorite_cities


@router.post("/favorites/sync", status_code=status.HTTP_200_OK)
async def sync_favorite_cities(session: SessionDep, current_user: CurrentUser):
    """
    Sync favorite cities for the user.
    """
    w = WeatherScraper(current_user.weather_id_token)
    favorite_cities = await w.get_user_favorite_cities()
    favorite_cities = await get_city_weathers(favorite_cities)

    # Format
    favorite_cities = [
        {
            "name": city["name"],
            "temperature": city["temperature_celsius"],
            "weather_condition": city["weather_condition"],
        }
        for city in favorite_cities
    ]

    cities_synced = create_or_update_cities(
        session=session, cities_data=favorite_cities
    )
    return cities_synced
