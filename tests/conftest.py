import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Set up test environment variables BEFORE any app imports
os.environ.update(
    {
        "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
        "OPENAI_API_KEY": "test-openai-key",
        "ACCESS_TOKEN_EXPIRE_MIN": "30",
        "DATABASE_URL": "sqlite://",  # Use in-memory database for tests
        "PATH_API_V1": "/api/v1",
    }
)

from app.api.deps import get_db
from app.main import app


@pytest.fixture(name="db_session")
def db_session_fixture():
    """Create a fresh database session for a test."""
    # Create an in-memory SQLite database for testing
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session
        # Clean up after the test
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(table.delete())
        session.commit()


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    """Create a test client for the FastAPI application."""

    # Override the database dependency to use our test session
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    # Clean up after the test
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_test_env():
    """Ensure test environment variables are set for all tests."""
    # Store original environment
    original_env = dict(os.environ)

    # Set test environment variables
    os.environ.update(
        {
            "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
            "OPENAI_API_KEY": "test-openai-key",
            "ACCESS_TOKEN_EXPIRE_MIN": "30",
            "DATABASE_URL": "sqlite://",
            "PATH_API_V1": "/api/v1",
        }
    )

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
