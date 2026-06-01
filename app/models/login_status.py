from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    model_validator,
)

MAX_FAILED_LOGIN_ATTEMPTS = 4


class LoginStatusModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(
        description="The user id associated with the login-status row.",
        examples=[1234],
        gt=0,
    )
    failed_login_attempts: int = Field(
        default=0,
        description="The number of failed login attempts in the active lockout window.",
        examples=[0, 3, 4],
        ge=0,
        le=MAX_FAILED_LOGIN_ATTEMPTS,
    )
    last_failed_login_attempt_at: datetime | None = Field(
        default=None,
        description="The timestamp for the most recent failed login attempt.",
        examples=[datetime(2026, 5, 28, 12, 0, 0)],
    )
    locked: StrictBool = Field(
        default=False,
        description="Whether the associated user account is locked.",
        examples=[False, True],
    )
    locked_at: datetime | None = Field(
        default=None,
        description="The timestamp when the associated user account was locked.",
        examples=[datetime(2026, 5, 28, 12, 3, 0)],
    )

    @model_validator(mode="after")
    def validate_failed_attempt_timestamp(self) -> "LoginStatusModel":
        if self.failed_login_attempts == 0 and self.last_failed_login_attempt_at:
            raise ValueError(
                "last_failed_login_attempt_at must be null when "
                "failed_login_attempts is 0."
            )
        if self.failed_login_attempts > 0 and self.last_failed_login_attempt_at is None:
            raise ValueError(
                "last_failed_login_attempt_at is required when "
                "failed_login_attempts is greater than 0."
            )
        return self


class UnlockLoginStatusByUserIdRequest(BaseModel):
    user_id: int = Field(
        description="The user id for the account to unlock.",
        examples=[1234],
        gt=0,
    )


class UnlockLoginStatusByUsernameRequest(BaseModel):
    username: str = Field(
        description="The username for the account to unlock.",
        examples=["jonydoe"],
        min_length=1,
    )
