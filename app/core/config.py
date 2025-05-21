from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PATH_API_V1: str = "/api/v1"

    class Config:
        case_sensitive = True


settings = Settings()
