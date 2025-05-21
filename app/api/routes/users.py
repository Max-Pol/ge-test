import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app import repository
from app.api.deps import CurrentUser, SessionDep
from app.core.auth import create_access_token, get_password_hash
from app.core.config import settings
from app.models import Token, UserSignup
from app.repository import UserNotFoundError
from app.weather.exceptions import (
    InvalidLoginCredentials,
    WeatherScraperRequestError,
)
from app.weather.scraper import WeatherScraper

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr


@router.post("/signup", response_model=UserResponse)
def register_user(session: SessionDep, user_signup: UserSignup) -> UserResponse:
    """
    Create new user without the need to be logged in.
    """
    user = repository.get_user_by_email(session=session, email=user_signup.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user = repository.create_user(
        session=session,
        email=user_signup.email,
        hashed_password=get_password_hash(user_signup.password),
    )
    return user


@router.post("/login")
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Raises:
        HTTPException:
            - 400: If email/password is incorrect
            - 401: If weather.com login fails
            - 500: If there's an internal server error
    """
    user = repository.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Update user's weather_id_token
    try:
        w = WeatherScraper()
        weather_id_token = await w.user_login(
            email=form_data.username, password=form_data.password
        )
        repository.update_user_weather_id_token(
            session=session, user_id=user.id, weather_id_token=weather_id_token
        )
    except InvalidLoginCredentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid weather.com credentials. Please check your email and password.",
        )
    except WeatherScraperRequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to authenticate with weather service: {str(e)}",
        )
    except UserNotFoundError:
        # This should never happen since we just authenticated the user
        raise HTTPException(
            status_code=500,
            detail="Internal server error: User not found after authentication",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)
    return Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires)
    )


@router.get("/me", response_model=UserResponse)
def test_token(current_user: CurrentUser) -> UserResponse:
    return current_user
