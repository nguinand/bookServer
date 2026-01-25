from pydantic import BaseModel, Field, ConfigDict


class UserStatusModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        0,
        description="The id of user status. Most likely comes from database",
        examples=[12],
        gt=0,
    )
    name: str = Field(
        description="The level name for the user", examples=["Platinum", "Bronze"]
    )
    level: int = Field(
        0, description="The level of the user", examples=[0, 1, 2, 3, 4, 5], gt=0
    )
    benefits: str = Field(
        "",
        description="The benefits of the user",
        examples=["Free tokens!", "random perk"],
    )
