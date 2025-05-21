from typing import Optional
from pydantic import BaseModel


class AvatarModel(BaseModel):
    id: int
    image_url: str
    description: Optional[str] = ""
