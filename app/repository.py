from sqlmodel import Session, select

from app.core.auth import verify_password
from app.models import City, User


class RepositoryError(Exception):
    """Base exception class for repository errors."""

    pass


class UserNotFoundError(RepositoryError):
    """Raised when a user cannot be found."""

    pass


def create_user(*, session: Session, email: str, hashed_password: str) -> User:
    user = User.model_validate(User(email=email, hashed_password=hashed_password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_id(*, session: Session, id: str) -> User | None:
    statement = select(User).where(User.id == id)
    return session.exec(statement).first()


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def update_user_weather_id_token(
    *, session: Session, user_id: str, weather_id_token: str
) -> User:
    """Update a user's weather ID token.

    Args:
        session: Database session
        user_id: ID of the user to update
        weather_id_token: New weather ID token to set

    Returns:
        User: The updated user object

    Raises:
        UserNotFoundError: If the user with the given ID cannot be found
    """
    user = get_user_by_id(session=session, id=user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")

    user.weather_id_token = weather_id_token
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_or_update_cities(*, session: Session, cities_data: list[dict]) -> list[City]:
    """
    Creates new cities or updates existing ones in the database from a list of city data.

    Args:
        session: The database session.
        cities_data: A list of dictionaries, where each dictionary represents
                     city data. Each dictionary should contain:
                     - 'name': str
                     - 'temperature': int
                     - 'weather_condition': str
                     - 'city_id': Optional[uuid.UUID] (for updates)

    Returns:
        A list of the created or updated City objects.
    """
    processed_cities = []
    for city_data in cities_data:
        name = city_data.get("name")
        temperature = city_data.get("temperature")
        weather_condition = city_data.get("weather_condition")

        if not all([name, temperature, weather_condition]):
            raise ValueError("Missing required fields")

        # Find city by name
        statement = select(City).where(City.name == name)
        city = session.exec(statement).first()

        if city:
            # Update existing city
            city.temperature = temperature
            city.weather_condition = weather_condition
        else:
            # Create new city
            city = City(
                name=name,
                temperature=temperature,
                weather_condition=weather_condition,
            )

        session.add(city)
        processed_cities.append(city)

    session.commit()
    for city in processed_cities:
        session.refresh(city)

    return processed_cities
