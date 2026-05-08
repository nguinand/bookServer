from fastapi import APIRouter, Depends

from app.api.user_status.create_user_status import router as create_user_status
from app.api.user_status.delete_user_status import router as delete_user_status
from app.api.user_status.get_user_status import router as get_user_status
from app.api.user_status.update_user_status import router as update_user_status
from app.utils.api_token import get_current_user

router = APIRouter(
    prefix="/user_status",
    tags=["user-status"],
    dependencies=[Depends(get_current_user)],
)

router.include_router(create_user_status)
router.include_router(get_user_status)
router.include_router(update_user_status)
router.include_router(delete_user_status)
