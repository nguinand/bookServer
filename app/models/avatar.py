from pydantic import BaseModel, ConfigDict, Field


class AvatarModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(
        None,
        gt=0,
        description="Unique ID of the avatar. Most likely comes from database.",
        examples=[1, 55, 332],
    )
    image_url: str = Field(
        description="Image URL for this avatar.",
        examples=[
            "https://myavatarsite.com/....",
        ],
    )
    description: str = Field(
        "",
        description="Description of this avatar.",
        examples=["This avatar has no description."],
    )
