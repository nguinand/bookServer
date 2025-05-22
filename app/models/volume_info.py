from pydantic import BaseModel, Field
from typing import List, Optional

from app.models.identifiers import IndustryIdentifier


class ImageLinksModel(BaseModel):
    small_thumbnail: Optional[str] = Field(None, alias="smallThumbnail")
    thumbnail: Optional[str] = Field(None)


class VolumeInfoModel(BaseModel):
    title: str = Field(..., description="Harry Potter and the Sorcerer's Stone")
    subtitle: Optional[str] = None
    authors: Optional[List[str]] = Field(default_factory=list)
    publisher: Optional[str] = Field(None, description="Pottermore Publishing")
    published_date: Optional[str] = Field(None, alias="publishedDate")
    description: Optional[str] = None
    page_count: Optional[int] = Field(None, alias="pageCount")
    categories: Optional[List[str]] = None
    average_rating: Optional[float] = Field(None, alias="averageRating")
    ratings_count: Optional[int] = Field(None, alias="ratingsCount")
    image_links: Optional[ImageLinksModel] = Field(None, alias="imageLinks")
    preview_link: Optional[str] = Field(None, alias="previewLink")
    industryIdentifiers: Optional[List[IndustryIdentifier]] = Field(
        None, alias="industryIdentifiers"
    )

    class Config:
        # extra = "allow"
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "Harry Potter and the Sorcerer's Stone",
                "subtitle": "Harry",
                "authors": ["J.K. Rowling"],
                "publisher": "Pottermore Publishing",
                "publishedDate": "2015-12-08",
                "description": "A magical story...",
                "pageCount": 311,
                "categories": ["Juvenile Fiction"],
                "averageRating": 4.5,
                "ratingsCount": 312,
                "imageLinks": {
                    "smallThumbnail": "http://example.com/small.jpg",
                    "thumbnail": "http://example.com/large.jpg",
                },
                "previewLink": "http://example.com/preview",
            }
        }
