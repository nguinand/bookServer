from fastapi import APIRouter

from app.api.bookcase.create_bookcase import router as create_bookcase
from app.api.bookcase.delete_bookcase import router as delete_bookcase
from app.api.bookcase.get_bookcase import router as get_bookcase
from app.api.bookcase.update_bookcase import router as update_bookcase

router = APIRouter()

router.include_router(create_bookcase)
router.include_router(get_bookcase)
router.include_router(update_bookcase)
router.include_router(delete_bookcase)
