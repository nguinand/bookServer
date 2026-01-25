from pydantic import BaseModel, Field, ConfigDict
from typing import List

from app.models.identifiers import IndustryIdentifier, IdentifierType


class ImageLinksModel(BaseModel):
    small_thumbnail: str | None = Field(
        None,
        alias="smallThumbnail",
        description="Small thumbnail of the book.",
        examples=["http://example.com/small.jpg"],
    )
    thumbnail: str | None = Field(
        None,
        description="Large thumbnail of the book.",
        examples=["http://example.com/large.jpg"],
    )


class VolumeInfoModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        description="The title of the book.",
        examples=["Harry Potter and the Sorcerer's Stone"],
    )
    subtitle: str | None = Field(
        None, description="Subtitle of the book.", examples=["Harry"]
    )
    authors: List[str] = Field(
        default_factory=list,
        description="Authors of the book.",
        examples=["J.K. Rowling"],
    )
    publisher: str | None = Field(
        None, description="The books publisher", examples=["Pottermore Publishing"]
    )
    published_date: str | None = Field(
        None,
        alias="publishedDate",
        description="Published date of the book.",
        examples=["2015-12-08"],
    )
    description: str | None = Field(
        None, description="The book description.", examples=["A magical story..."]
    )
    page_count: int | None = Field(
        0,
        alias="pageCount",
        description="Page count of the book.",
        examples=[1, 360],
        ge=0,
    )
    categories: List[str] = Field(
        default_factory=list,
        description="Categories of the book.",
        examples=[["Juvenile Fiction", "Horror"]],
    )
    average_rating: float | None = Field(
        None,
        alias="averageRating",
        description="Average rating of the book. Out of 5.0",
        examples=[4.5, 5.0],
        ge=0,
    )
    ratings_count: int | None = Field(
        None,
        alias="ratingsCount",
        description="Number of individual ratings of the book.",
        examples=[3, 565],
        ge=0,
    )
    image_links: ImageLinksModel | None = Field(
        None,
        alias="imageLinks",
        description="Image links model of the book.",
        json_schema_extra={
            "example": {
                "smallThumbnail": "https://example.com/small.jpg",
                "thumbnail": "https://example.com/large.jpg",
            }
        },
    )
    preview_link: str | None = Field(
        None,
        alias="previewLink",
        description="Preview link of the book. Shows page snippets.",
        examples=["https://example.com/preview"],
    )
    info_link: str | None = Field(
        None,
        alias="infoLink",
        description="Information link of the book. Brings up Google play description.",
        examples=["https://example.com/info"],
    )
    language: str | None = Field(
        None, description="Language of the book.", examples=["English", "Spanish"]
    )
    industryIdentifiers: List[IndustryIdentifier] | None = Field(
        None,
        alias="industryIdentifiers",
        description="Industry identifiers model of the book. ISBN 10 or 13",
        json_schema_extra={
            "examples": [{"type": IdentifierType.ISBN_10, "identifier": "1234567890"}]
        },
    )
    maturity_rating: str | None = Field(
        None, description="Maturity rating of the book.", examples=["NOT_MATURE"]
    )
