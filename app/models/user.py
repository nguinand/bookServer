from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="The id of the user", examples=[1234], gt=0)
    first_name: str = Field(
        description="The first name of the user", examples=["John", "Jane"]
    )
    last_name: str = Field(description="The last name of the user", examples=["Doe"])
    username: str = Field(description="The username of the user", examples=["jonydoe"])
    email: EmailStr = Field(
        description="The email address of the user", examples=["jdoe@gmail.com"]
    )
    password_hash: str = Field(
        description="The hashed password", examples=["qwerascvatgwerdy132412t3546r"]
    )  # I put random text here in the example.
    role: Literal["user", "admin"] = Field(
        default_value="user", description="The role of the user", examples=["user"]
    )
    avatar_id: int | None = Field(
        None, description="The id of the avatar", examples=[1234], gt=0
    )
    status_id: int | None = Field(
        None, description="The id of the avatar", examples=[1234], gt=0
    )
    created_at: datetime = Field(
        datetime.now(),
        description="The time the avatar was created",
        examples=[datetime(2020, 1, 1)],
    )
    last_login: datetime = Field(
        datetime.now(),
        description="The time the user last logged in",
        examples=[datetime(2020, 1, 1)],
    )
