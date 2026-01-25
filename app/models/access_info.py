from pydantic import BaseModel, Field, AliasChoices, StrictBool, ConfigDict


class FormatInfoModel(BaseModel):
    isAvailable: StrictBool = Field(
        False,
        description="Whether or not the book is available in this format",
        examples=[True, False],
    )
    acsTokenLink: str | None = Field(
        None,
        description="The token link to the pdf or epub",
        examples=["https://example.com/epub.acsm"],
    )

    model_config = ConfigDict(from_attributes=True)


class AccessInfoModel(BaseModel):
    country: str | None = Field(
        None,
        description="The country where this book is accessed.",
        examples=["US", "PE"],
    )
    viewability: str | None = Field(
        None,
        description="The viewability of the book. Could be partial or have no pages (electronic)",
        examples=["PARTIAL", "NO_PAGES"],
    )
    embeddable: StrictBool = Field(
        False,
        description="Whether or not the book is embedded in the book's web reader.",
        examples=[True, False],
    )
    public_domain: StrictBool = Field(
        False,
        alias="publicDomain",
        validation_alias=AliasChoices("publicDomain", "public_domain"),
        description="Whether or not the book has a public domain.",
        examples=[True, False],
    )
    epub: FormatInfoModel | None = Field(
        None,
        description="The epub format of the book. Extends from the FormatInfoModel",
        json_schema_extra={
            "example": {
                "isAvailable": True,
                "acsTokenLink": "https://example.com/epub.acsm",
            }
        },
    )
    pdf: FormatInfoModel | None = Field(
        None,
        description="The pdf format of the book. Extends from the FormatInfoModel",
        json_schema_extra={
            "example": {
                "isAvailable": True,
                "acsTokenLink": "https://example.com/epub.acsm",
            }
        },
    )
    web_reader_link: str | None = Field(
        None,
        alias="webReaderLink",
        validation_alias=AliasChoices("webReaderLink", "web_reader_link"),
        description="The web reader link of the book.",
        examples=["https://example.com/webreader_link"],
    )

    # Translates the pydantic model to the sqlalchemy ORM model
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
