from fastapi import APIRouter, Depends

from app.api.book_access.create_access_info import router as create_access_info
from app.api.book_access.delete_access_info import router as delete_access_info
from app.api.book_access.get_access_info import router as get_access_info
from app.api.book_access.update_access_info import router as update_access_info
from app.utils.api_token import get_current_user

router = APIRouter(
    prefix="/book_access",
    tags=["book-access"],
    dependencies=[Depends(get_current_user)],
)

router.include_router(create_access_info)
router.include_router(get_access_info)
router.include_router(update_access_info)
router.include_router(delete_access_info)
