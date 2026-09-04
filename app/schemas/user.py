from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    language: str = Field(
        default="en",
        pattern="^(en|te|hi)$"
    )


class LanguageUpdate(BaseModel):
    language: str = Field(
        pattern="^(en|te|hi)$"
    )