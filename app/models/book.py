from pydantic import BaseModel, Field, ConfigDict
from app.models.volume_info import VolumeInfoModel
from app.models.book_sale_info import BookSaleInfoModel
from app.models.access_info import AccessInfoModel


class BookModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    book_id: int | None = Field(
        default=None, gt=0, description="Book ID", examples=[1, 5, 99]
    )
    google_books_id: str = Field(
        alias="id",
        description="ID given from the google books api",
        examples=["wkNGAAAAYAAJ", "OWGH-FVGafEC"],
    )
    volume_info: VolumeInfoModel = Field(
        description="Information about the book",
        alias="volumeInfo",
        json_schema_extra={
            "example": {
                "title": "Harry Potter and the Sorcerer's Stone",
                "subtitle": "Harry",
                "authors": "J.K. Rowling",
                "publisher": "Pottermore Publishing",
                "published_date": "2015-12-08",
                "description": "description of book",
                "page_count": "233",
                "categories": ["Juvenile Fiction", "Horror"],
                "average_rating": 4.5,
                "ratings_count": 332,
                "info_link": "https://example.com/",
                "language": "English",
                "industryIdentifiers": {
                    "type": "isbn_10",
                    "identifier": "1234567890",
                },
                "maturity_rating": "NOT_MATURE",
            }
        },
    )
    sale_info: BookSaleInfoModel | None = Field(
        None,
        alias="saleInfo",
        description="Information about the sale",
        json_schema_extra={
            "example": {
                "book_id": 12,
                "country": "USA",
                "saleability": "NOT_FOR_SALE",
                "is_ebook": False,
                "list_price": {"amount": 5.99, "currencyCode": "USD"},
                "retail_price": {"amount": 5.99, "currencyCode": "USD"},
            },
            "buy_link": "https://example.com/",
        },
    )
    access_info: AccessInfoModel | None = Field(
        None,
        alias="accessInfo",
        description="How this book can be accessed.",
        json_schema_extra={
            "example": {
                "country": "USA",
                "viewability": "PARTIAL",
                "embeddable": True,
                "public_domain": True,
                "epub": {"isAvailable": True, "acsTokenLink": "https://example.com/"},
                "pdf": {"isAvailable": True, "acsTokenLink": "https://example.com/"},
                "web_reader_link": "https://example.com/",
            }
        },
    )
