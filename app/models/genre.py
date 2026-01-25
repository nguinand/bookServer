from pydantic import BaseModel, ConfigDict, Field


class GenreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="The id of the genre.", examples=[1234], gt=0)
    name: str = Field(
        description="The name of the genre.", examples=["Romance", "Comedy"]
    )
