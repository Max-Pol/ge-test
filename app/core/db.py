from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  # Import models to register them with SQLModel metadata
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)


def init_db(session: Session) -> None:
    # To simplify the process, we create the tables here.
    # In a real project, we would use migrations (with Alembic for instance).
    SQLModel.metadata.create_all(engine)
