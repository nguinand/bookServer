from typing import Optional
from pydantic import BaseModel


class UserStatusModel(BaseModel):
    id: int
    name: str
    level: int
    benefits: Optional[str] = ""
