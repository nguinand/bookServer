from fastapi import APIRouter, Depends

from app.api.user_book_state.create_user_book_state import (
    router as create_user_book_state,
)
from app.api.user_book_state.delete_user_book_state import (
    router as delete_user_book_state,
)
from app.api.user_book_state.get_user_book_state import router as get_user_book_state
from app.api.user_book_state.update_user_book_state import (
    router as update_user_book_state,
)
from app.utils.api_token import get_current_user

router = APIRouter(
    prefix="/user_book_state",
    tags=["user-book-state"],
    dependencies=[Depends(get_current_user)],
)

router.include_router(create_user_book_state)
router.include_router(get_user_book_state)
router.include_router(update_user_book_state)
router.include_router(delete_user_book_state)
