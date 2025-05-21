import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import User, UserSignup
from app.repository import get_user_by_email


def test_register_user_success(client: TestClient, db_session: Session):
    """Test successful user registration."""
    # Arrange
    user_data = UserSignup(email="test@example.com", password="testpassword123")

    # Act
    response = client.post("/api/v1/users/signup", json=user_data.model_dump())

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == user_data.email

    # Verify user was actually created in database
    user = get_user_by_email(session=db_session, email=user_data.email)
    assert user is not None
    assert user.email == user_data.email


def test_register_user_duplicate_email(client: TestClient, db_session: Session):
    """Test registration with an email that already exists."""
    # Arrange
    user_data = UserSignup(email="existing@example.com", password="testpassword123")

    # Create a user first
    client.post("/api/v1/users/signup", json=user_data.model_dump())

    # Act
    response = client.post("/api/v1/users/signup", json=user_data.model_dump())

    # Assert
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "The user with this email already exists in the system"
    )


def test_register_user_invalid_email(client: TestClient, db_session: Session):
    """Test registration with an invalid email format."""
    # Arrange
    user_data = {"email": "not-an-email", "password": "testpassword123"}

    # Act
    response = client.post("/api/v1/users/signup", json=user_data)

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.fixture(autouse=True)
def cleanup_database(db_session: Session):
    """Clean up the database after each test."""
    yield
    db_session.exec(User.__table__.delete())
    db_session.commit()
