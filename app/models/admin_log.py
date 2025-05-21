from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AdminLogsModel(BaseModel):
    id: Optional[int] = None
    event_type: str
    event_description: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
