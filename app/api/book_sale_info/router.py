from fastapi import APIRouter, Depends

from app.api.book_sale_info.create_book_sale_info import router as create_sale_info
from app.api.book_sale_info.delete_book_sale_info import router as delete_sale_info
from app.api.book_sale_info.get_book_sale_info import router as get_sale_info
from app.api.book_sale_info.update_book_sale_info import router as update_sale_info
from app.utils.api_token import get_current_user

router = APIRouter(
    prefix="/book_sale_info",
    tags=["book-sale-info"],
    dependencies=[Depends(get_current_user)],
)

router.include_router(create_sale_info)
router.include_router(get_sale_info)
router.include_router(update_sale_info)
router.include_router(delete_sale_info)
