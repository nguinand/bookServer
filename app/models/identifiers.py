from pydantic import BaseModel, Field


class IndustryIdentifier(BaseModel):
    type: str = Field(..., example="ISBN_13")
    identifier: str = Field(..., example="9781781100486")
