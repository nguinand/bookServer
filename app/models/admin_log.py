from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AdminEventType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    MODIFY = "modify"


class AdminLogsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Admin Log ID", examples=[1, 2, 5], gt=0)
    event_type: AdminEventType = Field(
        description="Admin event type",
        examples=["create", "update", "delete", "login", "logout", "modify"],
    )
    event_description: str = Field(
        description="Admin event description", examples=["Modified user status"]
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Admin event created time",
        examples=[datetime(2026, 4, 30, 12, 0, 0)],
    )


class GetAdminLogsRequest(BaseModel):
    start_time: datetime = Field(
        description="Inclusive start time for admin log filtering.",
        examples=[datetime(2026, 4, 1, 0, 0, 0)],
    )
    end_time: datetime = Field(
        description="Inclusive end time for admin log filtering.",
        examples=[datetime(2026, 4, 30, 23, 59, 59)],
    )
    limit: int = Field(
        default=100,
        description="Maximum number of admin logs to return.",
        examples=[100],
        ge=1,
    )
    offset: int = Field(
        default=0,
        description="Number of matching admin logs to skip.",
        examples=[0],
        ge=0,
    )

    @model_validator(mode="after")
    def validate_time_frame(self) -> "GetAdminLogsRequest":
        if self.end_time < self.start_time:
            raise ValueError("end_time must be greater than or equal to start_time.")
        return self


class GetAdminLogsResponse(BaseModel):
    logs: list[AdminLogsModel] = Field(
        description="The admin logs for the requested page."
    )
    limit: int = Field(description="Requested page size.", examples=[100], ge=1)
    offset: int = Field(description="Requested page offset.", examples=[0], ge=0)
    count: int = Field(description="Number of logs returned.", examples=[25], ge=0)
    total: int = Field(
        description="Total number of logs matching the time frame.",
        examples=[125],
        ge=0,
    )
