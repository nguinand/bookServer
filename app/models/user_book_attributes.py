from datetime import datetime

from pydantic import BaseModel, Field


# This is the USER input for the book.
class UserBookAttributesModel(BaseModel):
    id: int = Field(
        description="Id for the user given attributes. Most likely comes from the database.",
        examples=[1234],
        gt=0,
    )
    user_id: int = Field(
        description="The User associated with the given attribute.",
        examples=[1234],
        gt=0,
    )
    book_id: int = Field(
        description="The Book id associated with the given attribute",
        examples=[1234],
        gt=0,
    )
    rating: int = Field(
        description="Book rating given by the user", examples=[0, 5, 10], ge=0, lt=10
    )
    review_text: str = Field("", description="The review test for the book.")
    created_at: datetime = Field(
        datetime.now(),
        description="Date and time when the attribute was created.",
        examples=[datetime(2020, 1, 1)],
    )
    updated_at: datetime = Field(
        datetime.now(),
        description="Date and time when the attribute updated.",
        examples=[datetime(2020, 1, 1)],
    )
