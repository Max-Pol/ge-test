import uuid

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


class UserSignup(BaseModel):
    email: EmailStr
    password: str


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    weather_id_token: str | None = None


class City(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, max_length=255)
    temperature: int
    weather_condition: str = Field(max_length=100)


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenData(BaseModel):
    sub: str | None = None
