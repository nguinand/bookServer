from pydantic import BaseModel, Field
from typing import Optional
from app.models.volume_info import VolumeInfo
from app.models.sale_info import SaleInfo
from app.models.access_info import AccessInfo


class Book(BaseModel):
    google_books_id: str = Field(..., example="wrOQLV6xB-wC")
    volume_info: VolumeInfo = Field(..., alias="volumeInfo")
    sale_info: Optional[SaleInfo] = Field(None, alias="saleInfo")
    access_info: Optional[AccessInfo] = Field(None, alias="accessInfo")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "wrOQLV6xB-wC",
                "volume_info": {
                    "title": "Harry Potter and the Sorcerer's Stone",
                    "authors": ["J.K. Rowling"],
                    "publisher": "Pottermore Publishing",
                    "published_date": "2015-12-08",
                    "description": "A magical story...",
                    "page_count": 311,
                    "categories": ["Juvenile Fiction"],
                    "average_rating": 4.5,
                    "ratings_count": 312,
                    "image_links": {
                        "small_thumbnail": "http://example.com/small.jpg",
                        "thumbnail": "http://example.com/large.jpg"
                    },
                    "preview_link": "http://example.com/preview"
                },
                "sale_info": {
                    "country": "US",
                    "saleability": "FOR_SALE",
                    "is_ebook": True,
                    "list_price": {"amount": "11.99", "currencyCode": "USD"}
                },
                "access_info": {
                    "country": "US",
                    "viewability": "PARTIAL",
                    "embeddable": True,
                    "publicDomain": False,
                    "epub": {"isAvailable": True},
                    "pdf": {"isAvailable": False}
                }
            }
        }