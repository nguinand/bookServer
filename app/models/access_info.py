from typing import Optional
from pydantic import BaseModel, Field, AliasChoices


class FormatInfoModel(BaseModel):
    isAvailable: Optional[bool] = None
    acsTokenLink: Optional[str] = None

    model_config = {"populate_by_name": True, "from_attributes": True}


class AccessInfoModel(BaseModel):
    country: Optional[str] = None
    viewability: Optional[str] = None
    embeddable: Optional[bool] = None
    public_domain: Optional[bool] = Field(
        None,
        alias="publicDomain",
        validation_alias=AliasChoices("publicDomain", "public_domain"),
    )
    epub: Optional[FormatInfoModel] = None
    pdf: Optional[FormatInfoModel] = None
    web_reader_link: Optional[str] = Field(
        None,
        alias="webReaderLink",
        validation_alias=AliasChoices("webReaderLink", "web_reader_link"),
    )

    def to_orm_dict(self) -> dict:
        return {
            "country": self.country,
            "viewability": self.viewability,
            "embeddable": self.embeddable,
            "public_domain": self.public_domain,
            "epub_available": self.epub.isAvailable if self.epub else None,
            "epub_token_link": self.epub.acsTokenLink if self.epub else None,
            "pdf_available": self.pdf.isAvailable if self.pdf else None,
            "pdf_token_link": self.pdf.acsTokenLink if self.pdf else None,
            "web_reader_link": self.web_reader_link,
        }

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
