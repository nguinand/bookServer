from typing import Dict, Optional
from pydantic import BaseModel, Field


class AccessInfo(BaseModel):
    country: Optional[str] = None
    viewability: Optional[str] = None
    embeddable: Optional[bool] = None
    publicDomain: Optional[bool] = Field(None, alias="publicDomain")
    epub: Optional[Dict[str, bool]] = None
    pdf: Optional[Dict[str, bool]] = None


    class Config:
        json_schema_extra = {
            "example": {
                "country": "US",
                "viewability": "PARTIAL",
                "embeddable": True,
                "publicDomain": False,
                "epub": {"isAvailable": True},
                "pdf": {"isAvailable": False},
            }
        }