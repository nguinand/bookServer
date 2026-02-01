from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, StrictBool, ConfigDict


class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    INR = "INR"


# Unsure about naming
class PriceModel(BaseModel):
    amount: Decimal | None = Field(
        None, description="Cost of the book price.", examples=[Decimal("5.00")], ge=0
    )
    currencyCode: CurrencyCode | None = Field(
        None,
        description="Currency code following ISO 4217.",
        alias="currencyCode",
        examples=["USD", "EUR", "GBP", "JPY", "INR"],
    )

    @field_validator("currencyCode")
    def validate_currency(cls, currency: str | None) -> str | None:
        if currency is not None:
            allowed_currencies = {"USD", "EUR", "GBP", "JPY", "INR"}
            if currency not in allowed_currencies:
                raise ValueError(f"Invalid currency code: {currency}")
        return currency


class BookSaleInfoModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    book_id: int | None = Field(
        None,
        description="Book id of the book. From Google API, its missing. Would get set after the database creates entry.",
        examples=[1, 2, 55],
        gt=0,
    )
    country: str | None = Field(
        None, description="Sale country location.", examples=["USA"]
    )
    saleability: str | None = Field(
        None, description="Listed for sale or not.", examples=["NOT_FOR_SALE"]
    )
    is_ebook: StrictBool = Field(
        False,
        alias="isEbook",
        description="Whether the book is ebook or not.",
        examples=[True, False],
    )
    list_price: PriceModel | None = Field(
        None,
        alias="listPrice",
        description="Price listing of the book",
        json_schema_extra={"example": {"amount": 5.99, "currencyCode": "USD"}},
    )
    retail_price: PriceModel | None = Field(
        None,
        alias="retailPrice",
        description="Retail price of the book.",
        json_schema_extra={"example": {"amount": 5.99, "currencyCode": "USD"}},
    )
    buy_link: str | None = Field(
        None,
        alias="buyLink",
        description="Buy link of the book.",
        examples=["https://example.com/"],
    )
