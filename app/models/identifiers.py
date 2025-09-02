from enum import Enum
import re
from pydantic import BaseModel, Field, field_validator


class IdentifierType(str, Enum):
    ISBN_10 = "ISBN_10"
    ISBN_13 = "ISBN_13"


class IndustryIdentifier(BaseModel):
    type: IdentifierType
    identifier: str = Field(..., json_schema_extra={"example": "9781781100486"})

    @field_validator("identifier")
    @classmethod
    def validate_isbn(cls, value, info):
        """Validate ISBN-10 and ISBN-13 formats"""
        isbn_type = info.data["type"]

        # Validate ISBN-10
        if isbn_type == IdentifierType.ISBN_10:
            if not re.match(r"^\d{9}[\dX]$", value):
                raise ValueError(
                    "ISBN-10 must be 10 characters (digits or 'X' as checksum)"
                )

        # Validate ISBN-13
        elif isbn_type == IdentifierType.ISBN_13:
            if not re.match(r"^\d{13}$", value):
                raise ValueError("ISBN-13 must be exactly 13 digits")

        return value
