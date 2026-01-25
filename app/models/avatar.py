from pydantic import BaseModel, Field


class AvatarModel(BaseModel):
    id: int = Field(
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
