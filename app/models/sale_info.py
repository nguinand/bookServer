from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# Unsure about naming
class Price(BaseModel):
    amount: Optional[Decimal] = Field(
        None, gt=0, description="The optional price amount."
    )
    currencyCode: Optional[str] = Field(
        None, description="Currency code following ISO 4217."
    )

    # Currency validation with Pydantic v2 field validator
    @field_validator("currencyCode")
    def validate_currency(cls, currency: Optional[str]) -> Optional[str]:
        if currency is not None:
            allowed_currencies = {"USD", "EUR", "GBP", "JPY", "INR"}
            if currency not in allowed_currencies:
                raise ValueError(f"Invalid currency code: {currency}")
        return currency


class SaleInfo(BaseModel):
    country: Optional[str] = None
    saleability: Optional[str] = None
    is_ebook: Optional[bool] = Field(None, alias="isEbook")
    list_price: Optional[Price] = Field(None, alias="listPrice")
