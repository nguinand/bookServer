from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StrictBool


class UserLoginRequest(BaseModel):
    username: str = Field(
        description="The username for the account.",
        examples=["jonydoe"],
        min_length=1,
    )
    password: str = Field(
        description="The plaintext password for the account.",
        examples=["Apple"],
        min_length=7,
    )


class AuthenticationStatusResponse(BaseModel):
    user_id: int = Field(
        description="The authenticated user id.", gt=0, examples=[1234]
    )
    username: str = Field(
        description="The authenticated username.",
        examples=["jonydoe"],
    )
    authenticated: StrictBool = Field(
        description="Whether the user was successfully authenticated.",
        examples=[True],
    )
    details: str = Field(
        description="A summary of the authentication result.",
        examples=["User authenticated."],
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJI..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type",
        examples=["bearer"],
    )


class PasswordUpdateRequest(BaseModel):
    current_password: str = Field(
        description="The user's current plaintext password.",
        examples=["old_password"],
        min_length=7,
    )
    new_password: str = Field(
        description="The new plaintext password to store.",
        examples=["new_password"],
        min_length=7,
    )


class PasswordUpdateResponse(BaseModel):
    user_id: int = Field(description="The updated user id.", gt=0, examples=[1234])
    updated: StrictBool = Field(
        description="Whether the password update succeeded.",
        examples=[True],
    )
    details: str = Field(
        description="A summary of the password update result.",
        examples=["Password updated."],
    )


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = Field(
        default=None, description="The id of the user", examples=[1234], gt=0
    )
    first_name: str = Field(
        description="The first name of the user", examples=["John", "Jane"]
    )
    last_name: str = Field(description="The last name of the user", examples=["Doe"])
    username: str = Field(description="The username of the user", examples=["jonydoe"])
    email: EmailStr = Field(
        description="The email address of the user", examples=["jdoe@gmail.com"]
    )
    role: Literal["user", "admin"] = Field(
        default="user", description="The role of the user", examples=["user", "admin"]
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
    last_login: datetime | None = Field(
        datetime.now(),
        description="The time the user last logged in",
        examples=[datetime(2020, 1, 1)],
    )


class CreateUserRequest(BaseModel):
    user_model: UserModel = Field(description="The user pydantic model")
    password: str = Field(
        description="Plaintext password.", examples=["Apple"], min_length=7
    )
