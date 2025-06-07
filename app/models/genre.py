from typing import Optional
from pydantic import BaseModel


class GenreModel(BaseModel):
    id: Optional[int] = None
    name: str

    model_config = {"from_attributes": True}
