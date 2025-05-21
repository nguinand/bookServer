from typing import Optional
from pydantic import BaseModel, Field


class FormatInfoModel(BaseModel):
    isAvailable: Optional[bool] = None
    acsTokenLink: Optional[str] = None


class AccessInfoModel(BaseModel):
    country: Optional[str] = None
    viewability: Optional[str] = None
    embeddable: Optional[bool] = None
    publicDomain: Optional[bool] = Field(None, alias="publicDomain")
    epub: Optional[FormatInfoModel] = None
    pdf: Optional[FormatInfoModel] = None
    web_reader_link: Optional[str] = Field(None, alias="webReaderLink")

    class Config:
        json_schema_extra = {
            "example": {
                "country": "US",
                "viewability": "PARTIAL",
                "embeddable": True,
                "publicDomain": False,
                "epub": {
                    "isAvailable": True,
                    "acsTokenLink": "http://example.com/epub.acsm",
                },
                "pdf": {"isAvailable": False, "acsTokenLink": None},
                "webReaderLink": "http://example.com/webreader",
            }
        }
