from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    INR = "INR"


# Unsure about naming
class PriceModel(BaseModel):
    amount: Optional[Decimal] = Field(None, description="The optional price amount.")
    currencyCode: Optional[CurrencyCode] = Field(
        None, description="Currency code following ISO 4217.", alias="currencyCode"
    )

    @field_validator("currencyCode")
    def validate_currency(cls, currency: Optional[str]) -> Optional[str]:
        if currency is not None:
            allowed_currencies = {"USD", "EUR", "GBP", "JPY", "INR"}
            if currency not in allowed_currencies:
                raise ValueError(f"Invalid currency code: {currency}")
        return currency


class BookSaleInfoModel(BaseModel):
    id: Optional[int] = None
    book_id: int
    country: Optional[str] = None
    saleability: Optional[str] = None
    is_ebook: Optional[bool] = Field(None, alias="isEbook")
    list_price: Optional[PriceModel] = Field(None, alias="listPrice")
    retail_price: Optional[PriceModel] = Field(None, alias="retailPrice")
    buy_link: Optional[str] = Field(None, alias="buyLink")
    model_config = {"from_attributes": True, "populate_by_name": True}
