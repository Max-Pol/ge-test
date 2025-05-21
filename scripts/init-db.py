import logging
import os
from pathlib import Path

from sqlmodel import Session

# Set up test environment variables BEFORE any app imports
os.environ.update(
    {
        "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
    }
)
import app.models  # noqa
from app.core.config import settings
from app.core.db import engine, init_db

"""
This is a simple database initialization script for development purposes.
In a production environment, we would use Alembic for database migrations
to manage schema changes and data migrations in a more controlled way.
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def drop_db() -> None:
    # Extract the database path from the URL (remove sqlite:/// prefix)
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    if db_path.exists():
        logger.info(f"Dropping database at {db_path}")
        os.remove(db_path)
        logger.info("Database dropped successfully")
    else:
        logger.info("Database does not exist, skipping drop")


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Dropping existing database")
    drop_db()
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
