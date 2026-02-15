from fastapi import APIRouter

from app.api.user_book_attributes.create_user_book_attribute import (
    router as create_user_book_attribute,
)
from app.api.user_book_attributes.update_book_attribute import (
    router as update_user_book_attribute,
)

router = APIRouter()

router.include_router(create_user_book_attribute)
router.include_router(update_user_book_attribute)
