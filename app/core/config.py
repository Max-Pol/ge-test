from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PATH_API_V1: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///db.sqlite3"
    ACCESS_TOKEN_EXPIRE_MIN: int = 60 * 24

    # Secrets (loaded from env var)
    OPENAI_API_KEY: str
    JWT_SECRET_KEY: str

    class Config:
        case_sensitive = True


settings = Settings()
