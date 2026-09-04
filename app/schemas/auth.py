from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    mobile: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=6, max_length=100)
    language: str = "en"


class UserLogin(BaseModel):
    mobile: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    