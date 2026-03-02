from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.book import BookModel


class BookcaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = Field(
        default=None,
        gt=0,
        description="The id of the bookcase. Most likely from the database",
        examples=[99],
    )
    user_id: int = Field(
        gt=0,
        description="The user id for the person who owns the bookcase",
        examples=[99],
    )
    name: str = Field(
        description="The name of the bookcase",
        examples=["Fantasy", "My first bookcase"],
    )
    created_at: datetime = Field(
        datetime.now(),
        description="The date and time the bookcase was created",
        examples=[datetime.now()],
    )
    books: list[BookModel] = Field(
        default_factory=list,
        description="List of that are listed in the bookcase.",
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "bio": "British author best known for the Harry Potter series.",
                    "name": "J.K. Rowling",
                    "books": [
                        {
                            "id": 99,
                            "google_books_id": "wkNGAAAAYAAJ",
                            "volumeInfo": {
                                "title": "Harry Potter and the Sorcerer's Stone",
                                "subtitle": "Harry",
                                "authors": ["J.K. Rowling"],
                                "publisher": "Pottermore Publishing",
                                "publishedDate": "2015-12-08",
                                "description": "description of book",
                                "pageCount": 233,
                                "categories": ["Juvenile Fiction", "Horror"],
                                "averageRating": 4.5,
                                "ratingsCount": 332,
                                "imageLinks": {
                                    "smallThumbnail": "http://example.com/small.jpg",
                                    "thumbnail": "http://example.com/large.jpg",
                                },
                                "previewLink": "https://example.com/preview",
                                "infoLink": "https://example.com/",
                                "language": "en",
                                "industryIdentifiers": [
                                    {"type": "ISBN_10", "identifier": "1234567890"},
                                    {"type": "ISBN_13", "identifier": "9781234567897"},
                                ],
                                "maturity_rating": "NOT_MATURE",
                            },
                            "saleInfo": {
                                "id": 1,
                                "book_id": 99,
                                "country": "USA",
                                "saleability": "NOT_FOR_SALE",
                                "isEbook": False,
                                "listPrice": {"amount": 5.99, "currencyCode": "USD"},
                                "retailPrice": {"amount": 5.99, "currencyCode": "USD"},
                                "buyLink": "https://example.com/",
                            },
                            "accessInfo": {
                                "country": "USA",
                                "viewability": "PARTIAL",
                                "embeddable": True,
                                "publicDomain": True,
                                "epub": {
                                    "isAvailable": True,
                                    "acsTokenLink": "https://example.com/epub.acsm",
                                },
                                "pdf": {
                                    "isAvailable": True,
                                    "acsTokenLink": "https://example.com/pdf.acsm",
                                },
                                "webReaderLink": "https://example.com/webreader",
                            },
                        }
                    ],
                }
            ],
        },
    )
