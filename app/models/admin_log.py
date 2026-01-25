from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class AdminEventType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    MODIFY = "modify"


class AdminLogsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(desription="Admin Log ID", examples=[1, 2, 5], gt=0)
    event_type: AdminEventType = Field(
        description="Admin event type",
        examples=["create", "update", "delete", "login", "logout", "modify"],
    )
    event_description: str = Field(
        description="Admin event description", example="Modified user status"
    )
    created_at: datetime = Field(
        datetime.now(),
        description="Admin event created time",
        examples=[datetime.now()],
    )
